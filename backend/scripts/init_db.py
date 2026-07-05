from app.db import Base, engine
from app import models  # noqa: F401  (모델 등록을 위해 import)


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("테이블 생성 완료")


if __name__ == "__main__":
    main()
