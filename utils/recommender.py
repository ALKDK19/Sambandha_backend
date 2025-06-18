from typing import List, Dict
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.engagement import Recommendation
from app.models.interaction import Like
from app.models.preference import Preference
from app.models.profile import Profile
from app.models.security import BlockedUser
from app.models.user import User
from app.schemas.engagement import RecommendationCreate


class Recommender:
    def __init__(self, db: Session):
        self.db = db

    def hybrid_recommendation(self, user_id: int, limit: int = 10) -> List[RecommendationCreate]:
        """
        Hybrid recommendation combining content-based and collaborative filtering
        """
        # Content-based recommendations
        content_recs = self.content_based_recommendation(user_id, limit * 2)

        # Collaborative filtering recommendations
        collab_recs = self.collaborative_filtering(user_id, limit * 2)

        # Combine and deduplicate recommendations
        all_recs = {}

        # Add content-based recommendations with weight
        for rec in content_recs:
            if rec.recommended_user_id not in all_recs:
                all_recs[rec.recommended_user_id] = rec
                all_recs[rec.recommended_user_id].recommendation_score *= 0.6  # Weight for content-based
            else:
                all_recs[rec.recommended_user_id].recommendation_score += rec.recommendation_score * 0.6

        # Add collaborative recommendations with weight
        for rec in collab_recs:
            if rec.recommended_user_id not in all_recs:
                all_recs[rec.recommended_user_id] = rec
                all_recs[rec.recommended_user_id].recommendation_score *= 0.4  # Weight for collaborative
            else:
                all_recs[rec.recommended_user_id].recommendation_score += rec.recommendation_score * 0.4

        # Convert to list and sort by combined score
        combined_recs = list(all_recs.values())
        combined_recs.sort(key=lambda x: x.recommendation_score, reverse=True)

        return combined_recs[:limit]

    def content_based_recommendation(self, user_id: int, limit: int = 10) -> List[RecommendationCreate]:
        """
        Content-based recommendation using user profiles and preferences
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return []

        user_profile = self.db.query(Profile).filter(Profile.user_id == user_id).first()
        user_pref = self.db.query(Preference).filter(Preference.user_id == user_id).first()

        if not user_profile:
            return []

        # Get all active users who are not blocked
        all_users = self.db.query(User).filter(
            User.user_id != user_id,
            User.account_status == 'active'
        ).all()

        recommendations = []
        for other_user in all_users:
            # Skip if already recommended
            existing_rec = self.db.query(Recommendation).filter(
                Recommendation.user_id == user_id,
                Recommendation.recommended_user_id == other_user.user_id
            ).first()

            if existing_rec:
                continue

            # Skip if blocked
            blocked = self.db.query(BlockedUser).filter(
                ((BlockedUser.blocker_user_id == user_id) & (BlockedUser.blocked_user_id == other_user.user_id)) |
                ((BlockedUser.blocker_user_id == other_user.user_id) & (BlockedUser.blocked_user_id == user_id))
            ).first()

            if blocked:
                continue

            other_profile = self.db.query(Profile).filter(Profile.user_id == other_user.user_id).first()
            if not other_profile:
                continue

            # Calculate similarity score
            score = self.calculate_content_similarity(user_profile, other_profile, user_pref)

            if score > 0.3:  # Only consider recommendations with at least 30% similarity
                recommendations.append(RecommendationCreate(
                    user_id=user_id,
                    recommended_user_id=other_user.user_id,
                    recommendation_score=score,
                    reason="Content-based similarity"
                ))

        # Sort by score and limit results
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
        return recommendations[:limit]

    def calculate_content_similarity(self, profile1: Profile, profile2: Profile, pref1: Preference = None) -> float:
        """
        Calculate similarity between two profiles based on content
        """
        score = 0.0

        # Define attribute weights
        attribute_weights = {
            'religion_text': 0.15,
            'caste_text': 0.1,
            'education_level_text': 0.1,
            'profession_text': 0.1,
            'city_text': 0.05,
            'district_text': 0.05,
            'hobbies_interests': 0.1,
            'annual_salary_npr': 0.05,
            'rashi': 0.1,
            'nakshatra': 0.1,
            'manglik_status': 0.1
        }

        # Calculate similarity for each attribute
        for attr, weight in attribute_weights.items():
            val1 = getattr(profile1, attr, None)
            val2 = getattr(profile2, attr, None)

            if val1 and val2:
                if attr == 'hobbies_interests':
                    # For hobbies, calculate Jaccard similarity
                    hobbies1 = set(val1.split(','))
                    hobbies2 = set(val2.split(','))
                    intersection = len(hobbies1.intersection(hobbies2))
                    union = len(hobbies1.union(hobbies2))
                    if union > 0:
                        similarity = intersection / union
                        score += similarity * weight
                else:
                    if val1 == val2:
                        score += weight

        # Apply preference filters if available
        if pref1:
            # Age filter
            if profile2.date_of_birth:
                age = self.calculate_age(profile2.date_of_birth)
                if pref1.min_age and age < pref1.min_age:
                    return 0.0
                if pref1.max_age and age > pref1.max_age:
                    return 0.0

            # Height filter
            if profile2.height_cm:
                if pref1.min_height_cm and profile2.height_cm < pref1.min_height_cm:
                    return 0.0
                if pref1.max_height_cm and profile2.height_cm > pref1.max_height_cm:
                    return 0.0

            # Religion and caste filters
            if pref1.preferred_religions_text and profile2.religion_text:
                if profile2.religion_text not in pref1.preferred_religions_text.split(','):
                    return 0.0

            if pref1.preferred_castes_text and profile2.caste_text:
                if profile2.caste_text not in pref1.preferred_castes_text.split(','):
                    return 0.0

        return min(max(score, 0.0), 1.0)

    def calculate_age(self, dob) -> int:
        from datetime import datetime
        today = datetime.today().date()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def collaborative_filtering(self, user_id: int, limit: int = 10) -> List[RecommendationCreate]:
        """
        Collaborative filtering based on user interactions (likes)
        """
        # Get all likes by the user
        user_likes = self.db.query(Like).filter(Like.liker_user_id == user_id).all()

        if not user_likes:
            return []

        # Find users who liked the same profiles
        similar_users = {}
        for like in user_likes:
            # Get users who also liked this profile
            common_likers = self.db.query(Like).filter(
                Like.liked_user_id == like.liked_user_id,
                Like.liker_user_id != user_id
            ).all()

            for common_like in common_likers:
                if common_like.liker_user_id not in similar_users:
                    similar_users[common_like.liker_user_id] = 1
                else:
                    similar_users[common_like.liker_user_id] += 1

        if not similar_users:
            return []

        # Sort similar users by number of common likes
        sorted_similar_users = sorted(similar_users.items(), key=lambda x: x[1], reverse=True)

        # Get recommendations from top similar users
        recommendations = []
        for similar_user_id, _ in sorted_similar_users[:5]:  # Top 5 similar users
            # Get likes by similar user that the current user hasn't liked
            similar_user_likes = self.db.query(Like).filter(
                Like.liker_user_id == similar_user_id,
                Like.liked_user_id.notin_([like.liked_user_id for like in user_likes])
            ).all()

            for like in similar_user_likes:
                # Skip if already recommended
                existing_rec = self.db.query(Recommendation).filter(
                    Recommendation.user_id == user_id,
                    Recommendation.recommended_user_id == like.liked_user_id
                ).first()

                if existing_rec:
                    continue

                # Skip if blocked
                blocked = self.db.query(BlockedUser).filter(
                    ((BlockedUser.blocker_user_id == user_id) & (BlockedUser.blocked_user_id == like.liked_user_id)) |
                    ((BlockedUser.blocker_user_id == like.liked_user_id) & (BlockedUser.blocked_user_id == user_id))
                ).first()

                if blocked:
                    continue

                # Add recommendation with weight based on similarity
                recommendations.append(RecommendationCreate(
                    user_id=user_id,
                    recommended_user_id=like.liked_user_id,
                    recommendation_score=min(similar_users[similar_user_id] / len(user_likes), 1.0),
                    reason=f"Recommended by users with similar preferences"
                ))

        # Sort by score and limit results
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
        return recommendations[:limit]