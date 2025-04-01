import pytest

from hermes.core.Contact import Contact
from hermes.core.KBucket import KBucket
from hermes.core.Support import K_VAL


def test_kbucket_full():
    k = KBucket()
    for i in range(K_VAL):
        k.add_contact(Contact(None, i))

    with pytest.raises(Exception):
        k.add_contact(Contact(None, K_VAL+1))
