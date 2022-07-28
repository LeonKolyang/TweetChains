from datetime import datetime
import logging

from bson import ObjectId

from app.core import di
from app.db.db import get_database
from app.db.db_utils import connect_to_mongo, close_mongo_connection

from app.source.timeslots.timeslot_handling import add_timeslot, delete_timeslot

LOGGER = logging.getLogger(__name__)

TEST_USER_ID = "test_user_1"

class TestClassTimeslots:
    @classmethod
    def setup_class(self):
        """ setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        connect_to_mongo()
        self.db = get_database(test_instance=True)

    @classmethod
    def teardown_class(self):
        """ teardown any state that was previously setup with a call to
        setup_class.
        """
        self.db.drop_collection("timeslots")
        close_mongo_connection()

    def test_add_timeslot(self):
        timestamp = datetime.utcnow()
        insert_id = add_timeslot(timestamp, TEST_USER_ID, self.db)
        if insert_id:
            LOGGER.info(f"Generated test timestamp with id {insert_id}")
        assert isinstance(insert_id, ObjectId)

    def test_delete_timeslot(self):
        timestamp = datetime.utcnow()
        insert_id = add_timeslot(timestamp, TEST_USER_ID, self.db)
        
        delete_status = delete_timeslot(str(insert_id), self.db)
        assert delete_status == True