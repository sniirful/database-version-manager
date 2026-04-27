# Database Version Manager

This project is a tool that helps you easily define your database structure using versioning. For this, it needs to be included in your own project(s).

It currently only supports MySQL.

### Purpose

Normally, when creating an SQL database, you can define in a file the initial structure. When you later need to modify it, you have to perform raw queries that are often hardly tracked, or you end up writing your own database version manager in the app.

This project solves this problem by allowing you to version your database structure. `v1` being the initial version, you can add later versions each performing their own edits to the database.

**For example**:

- You create `v1`. It defines some tables and some data.
- The user runs `v1` and thus creates those tables and data on their system.
- You now create `v2`, you change the tables.
- The user that already has `v1` will now only change their existing tables. The user who instead runs the app for the first time, will create the initial tables and data and then changes it.

### How to use

- Create a folder in your project, e.g. `database-versioning/`.
- From inside that folder, run:
  ```bash
  git submodule add https://github.com/sniirful/database-version-manager.git database_version_manager
  ```
- Add the versioning files like so:
  ```py
  from database_version_manager import get_database_transaction


  def main():
      transaction = get_database_transaction(version=your_file_version)
      #
      # Your code here.
      #
      transaction.commit()


  if __name__ == "__main__":
      main()
  ```
- Add the following to your `docker-compose.yaml`:
  ```yaml
  services:

    # ...

    database:
      # ...
      healthcheck:
        test: [ "CMD", "mysqladmin", "ping", "-h", "localhost", "-uroot", "-proot" ]
        interval: 3s
        timeout: 3s
        retries: 30

    # ...

    database-versioning:
      build:
        context: ./database-versioning
        dockerfile: ./database_version_manager/Dockerfile
      environment:
        HOST: database
        PORT: 3306
        USERNAME: root
        PASSWORD: root
      depends_on:
        database:
          condition: service_healthy
  ```

You can also look at this repository as an example, though it's standalone and not added as a submodule.
