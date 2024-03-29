from random import randint
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.sql import exists

from .connection import local_session
from .models import Game
from .models import User


class DBSession:
    """connection to db"""

    @local_session
    def get_game_names(
        self,
        session,
        game_type=None,
        kids_age=None,
        kids_amount=None,
        location=None,
        props=None,
    ) -> list:
        """list of games by requested parameters"""

        games = session.query(Game.id, Game.name)

        if game_type is not None:
            games = games.filter(
                or_(Game.game_type.contains(f"%{game_type}%"), Game.game_type.is_(None))
            )

        if kids_amount is not None:
            games = games.filter(
                or_(
                    Game.kids_amount.contains(f"%{kids_amount}%"),
                    Game.kids_amount.is_(None),
                )
            )

        if location is not None:
            games = games.filter(
                or_(Game.location.contains(f"%{location}%"), Game.location.is_(None))
            )

        if props is not None:
            games = games.filter(
                or_(Game.props.contains(f"%{props}%"), Game.props.is_(None))
            )

        if kids_age is not None:
            games = games.filter(
                or_(Game.kids_age.contains(kids_age), Game.kids_age.is_(None))
            )
        return games.all()

    @local_session
    def get_game_description(self, session, name: str) -> str:
        """returns game description by it's name and lang"""

        game_data = [Game.description, Game.name]
        if len(name) > 60:
            name = name[:60]
        description = (
            session.query(game_data[0])
            .filter(game_data[1].contains(f"%{name}%"))
            .first()
        )
        return description[0] if description else ""

    @local_session
    def get_random_game_description(self, session) -> str:  # lang_ru: int = 0
        """returns random game description by lang"""
        query = session.query(Game.description)
        game = query.filter(Game.id == randint(1, session.query(Game).count())).first()
        return game[0]

    @local_session
    def delete_games(self, session) -> int:
        games_count = session.query(Game).count()
        session.query(Game).delete()
        session.commit()
        return games_count

    @local_session
    def set_games(self, session, games: list):
        objects = [
            Game(
                name=game[0][: game[0].find("\n")],
                description=game[0],
                game_type=game[1],
                kids_amount=game[2],
                kids_age=game[3],
                location=game[4],
                props=game[5],
            )
            for game in games
        ]
        session.bulk_save_objects(objects)
        session.commit()

    @local_session
    def authorize_user(self, session, chat_id: int) -> User:
        user = session.query(User).get(chat_id)
        if not user:
            user = self.create_user(chat_id)
        user.is_registered = True
        session.commit()
        return user

    @local_session
    def create_user(
        self, session, chat_id: int, language: Optional[int] = None
    ) -> User:
        user = session.query(User).get(chat_id)
        if not user:
            user = User(chat_id=chat_id, is_registered=False)
            if language in (0, 1):
                user.language = language
            session.add(user)
            session.commit()
        return user

    @local_session
    def check_user(self, session, chat_id: int) -> bool:
        user = session.query(User).get(chat_id)
        if user:
            return user.is_registered
        return False


db_interface = DBSession()
