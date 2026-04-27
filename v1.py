from common import get_database_transaction


def main():
    transaction = get_database_transaction(version=1)

    transaction.run_sql("CREATE DATABASE IF NOT EXISTS test")
    transaction.run_sql("USE test")

    transaction.run_sql(
        """
        CREATE TABLE test
        (
            test INT PRIMARY KEY
        )
        """
    )
    transaction.run_sql(
        """
        INSERT INTO test (test)
        VALUES (1)
        """
    )

    transaction.commit()


if __name__ == "__main__":
    main()
