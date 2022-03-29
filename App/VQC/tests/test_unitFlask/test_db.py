import pytest

from app import db

"""
Check whether it was possible to connect to db and test queries
Additionally test behaviour when it is not possible to connect with db. 
"""


@pytest.mark.db
def test_db(app):
    db.mongo_db.connect_db(app)

    assert db.mongo_db.connection.db is not None
    print(db.mongo_db.connection.db)
    assert "templates" in db.mongo_db.connection.db.list_collection_names()
    # For db connection to work we need to have such collection
    assert db.mongo_db.get_template(0) == "test"
    assert len(db.mongo_db.get_all_templates()) > 0

    # Setting not existing database then there won't be templates collection and everything will fail
    # So we nned to raise an exception
    with pytest.raises(SystemExit) as excinfo:
        app.config["DB"]["db"] = "NotBosch"
        db.mongo_db.connect_db(app)

    assert "There is no templates" in str(excinfo.value)

    # If some authentication data is wrong then we won't be able to connect with database we catch it
    # and raise some simpler exception
    # ! right now we don't have any authentication for our local db so there is nothing to check here
    # with pytest.raises(SystemExit) as excinfo:
    #     app.config["DB"]["host_name"] = "192.123.123.123"  # Some for sure bad url
    #     db.mongo_db.connect_db(app)

    # assert "Could not establish" in str(excinfo.value)
