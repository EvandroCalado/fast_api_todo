from sqlalchemy import select

from fast_api_todo.models import User


def test_create_user(session):
    user = User(
        username='evandro', email='evandro@gmail.com', password='123456'
    )

    session.add(user)
    session.commit()

    result = session.scalar(
        select(User).where(User.email == 'evandro@gmail.com')
    )

    assert result.id == 1
