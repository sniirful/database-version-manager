from . import get_database_transaction


def main():
    transaction = get_database_transaction(version=2)

    transaction.run_sql("USE test")
    transaction.run_sql(
        """
        INSERT INTO test (test)
        VALUES (2)
        """
    )

    transaction.commit()


if __name__ == "__main__":
    main()
