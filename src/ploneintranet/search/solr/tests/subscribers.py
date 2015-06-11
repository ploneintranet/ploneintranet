"""Ensure Solr indexing takes place in tests."""
import transaction


def on_tests_modify_content(obj, event):
    """Required to force Solr indexing in object modifications."""
    transaction.commit()


def on_tests_delete_content(obj, event):
    """Required to force Solr indexing object deletions."""
    transaction.commit()


def on_tests_add_content(obj, event):
    """Required to force Solr indexing object additions."""
    transaction.commit()


def on_tests_transition_content(obj, event):
    """Required to force review_state transistions."""
    obj.reindexObject()
    transaction.commit()
