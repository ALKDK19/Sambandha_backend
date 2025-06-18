import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.engagement import Notification
from app.models.interaction import Like, Match, Chat
from app.models.preference import Preference
from app.models.profile import Profile
from app.models.security import BlockedUser
from app.models.user import User
from app.schemas.engagement import RecommendationCreate


class MatchMaker:
    def __init__(self, db: Session):
        self.db = db

    def calculate_compatibility_score(self, user1: User, user2: User) -> float:
        """
        Calculate compatibility score between two users based on:
        - Profile attributes
        - Preferences
        - Interactions (likes, visits)
        """
        score = 0.0

        # Get profiles and preferences
        profile1 = self.db.query(Profile).filter(Profile.user_id == user1.user_id).first()
        profile2 = self.db.query(Profile).filter(Profile.user_id == user2.user_id).first()
        pref1 = self.db.query(Preference).filter(Preference.user_id == user1.user_id).first()
        pref2 = self.db.query(Preference).filter(Preference.user_id == user2.user_id).first()

        if not profile1 or not profile2:
            return 0.0

        # 1. Check if users meet each other's basic preferences
        if pref1 and pref2:
            # Check age preferences
            if profile2.date_of_birth:
                age2 = self.calculate_age(profile2.date_of_birth)
                if pref1.min_age and age2 < pref1.min_age:
                    return 0.0
                if pref1.max_age and age2 > pref1.max_age:
                    return 0.0

            if profile1.date_of_birth:
                age1 = self.calculate_age(profile1.date_of_birth)
                if pref2.min_age and age1 < pref2.min_age:
                    return 0.0
                if pref2.max_age and age1 > pref2.max_age:
                    return 0.0

            # Check height preferences
            if profile2.height_cm:
                if pref1.min_height_cm and profile2.height_cm < pref1.min_height_cm:
                    return 0.0
                if pref1.max_height_cm and profile2.height_cm > pref1.max_height_cm:
                    return 0.0

            if profile1.height_cm:
                if pref2.min_height_cm and profile1.height_cm < pref2.min_height_cm:
                    return 0.0
                if pref2.max_height_cm and profile1.height_cm > pref2.max_height_cm:
                    return 0.0

            # Check religion and caste preferences
            if pref1.preferred_religions_text and profile2.religion_text:
                if profile2.religion_text not in pref1.preferred_religions_text.split(','):
                    return 0.0

            if pref2.preferred_religions_text and profile1.religion_text:
                if profile1.religion_text not in pref2.preferred_religions_text.split(','):
                    return 0.0

            if pref1.preferred_castes_text and profile2.caste_text:
                if profile2.caste_text not in pref1.preferred_castes_text.split(','):
                    return 0.0

            if pref2.preferred_castes_text and profile1.caste_text:
                if profile1.caste_text not in pref2.preferred_castes_text.split(','):
                    return 0.0

        # 2. Calculate score based on matching attributes
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

        # 3. Boost score if there are mutual likes
        mutual_like = self.db.query(Like).filter(
            ((Like.liker_user_id == user1.user_id) & (Like.liked_user_id == user2.user_id)) |
            ((Like.liker_user_id == user2.user_id) & (Like.liked_user_id == user1.user_id))
        ).count()

        if mutual_like >= 2:
            score += 0.3  # Significant boost for mutual likes

        # Ensure score is between 0 and 1
        score = min(max(score, 0.0), 1.0)

        return score

    def calculate_age(self, dob: datetime.date) -> int:
        today = datetime.today().date()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def find_potential_matches(self, user_id: int, limit: int = 10) -> List[RecommendationCreate]:
        """
        Find potential matches for a user using hybrid filtering (content + collaborative)
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return []

        # Get all active users who are not blocked and not already matched
        all_users = self.db.query(User).filter(
            User.user_id != user_id,
            User.account_status == 'active'
        ).all()

        # Calculate scores for each potential match
        recommendations = []
        for potential_match in all_users:
            # Skip if already matched
            existing_match = self.db.query(Match).filter(
                ((Match.user1_id == user_id) & (Match.user2_id == potential_match.user_id)) |
                ((Match.user1_id == potential_match.user_id) & (Match.user2_id == user_id))
            ).first()

            if existing_match:
                continue

            # Skip if blocked
            blocked = self.db.query(BlockedUser).filter(
                ((BlockedUser.blocker_user_id == user_id) & (BlockedUser.blocked_user_id == potential_match.user_id)) |
                ((BlockedUser.blocker_user_id == potential_match.user_id) & (BlockedUser.blocked_user_id == user_id))
            ).first()

            if blocked:
                continue

            # Calculate compatibility score
            score = self.calculate_compatibility_score(user, potential_match)

            if score > 0.3:  # Only consider matches with at least 30% compatibility
                recommendations.append(RecommendationCreate(
                    user_id=user_id,
                    recommended_user_id=potential_match.user_id,
                    recommendation_score=score,
                    reason=f"Compatibility score: {score:.0%}"
                ))

        # Sort by score and limit results
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
        return recommendations[:limit]

    def create_match_if_compatible(self, user1_id: int, user2_id: int) -> Optional[Match]:
        """
        Check if two users are compatible and create a match if they are
        """
        user1 = self.db.query(User).filter(User.user_id == user1_id).first()
        user2 = self.db.query(User).filter(User.user_id == user2_id).first()

        if not user1 or not user2:
            return None

        # Check if already matched
        existing_match = self.db.query(Match).filter(
            ((Match.user1_id == user1_id) & (Match.user2_id == user2_id)) |
            ((Match.user1_id == user2_id) & (Match.user2_id == user1_id))
        ).first()

        if existing_match:
            return existing_match

        # Calculate compatibility score
        score = self.calculate_compatibility_score(user1, user2)

        # Create match if score is above threshold or there are mutual likes
        if score >= 0.7:  # 70% compatibility threshold
            # Check for mutual likes
            mutual_likes = self.db.query(Like).filter(
                ((Like.liker_user_id == user1_id) & (Like.liked_user_id == user2_id)) |
                ((Like.liker_user_id == user2_id) & (Like.liked_user_id == user1_id))
            ).count()

            if mutual_likes >= 2 or score >= 0.8:
                # Create new match
                new_match = Match(
                    user1_id=min(user1_id, user2_id),
                    user2_id=max(user1_id, user2_id),
                    compatibility_score=score,
                    match_status='active'
                )
                self.db.add(new_match)
                self.db.commit()
                self.db.refresh(new_match)

                # Create chat
                new_chat = Chat(
                    match_id=new_match.match_id,
                    initiator_user_id=user1_id,
                    receiver_user_id=user2_id
                )
                self.db.add(new_chat)
                self.db.commit()

                # Create notifications
                self.create_match_notification(user1_id, user2_id, new_match.match_id)
                self.create_match_notification(user2_id, user1_id, new_match.match_id)

                return new_match

        return None

    def create_match_notification(self, user_id: int, matched_user_id: int, match_id: int):
        """
        Create a notification for a new match
        """
        matched_user = self.db.query(User).join(Profile).filter(User.user_id == matched_user_id).first()
        if not matched_user or not matched_user.profile:
            return

        notification = Notification(
            user_id=user_id,
            notification_type='new_match',
            title="New Match!",
            message_body=f"You have a new match with {matched_user.profile.first_name}!",
            related_entity_type='match',
            related_entity_id=match_id
        )
        self.db.add(notification)
        self.db.commit()