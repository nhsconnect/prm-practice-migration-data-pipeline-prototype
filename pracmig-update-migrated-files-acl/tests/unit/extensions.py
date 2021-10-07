from moto.s3.models import *

def get_canned_acl(acl):
    owner_grantee = FakeGrantee(id=OWNER)
    grants = []
    if acl == "private":
        pass  # no other permissions
    elif acl == "public-read":
        grants.append(FakeGrant([ALL_USERS_GRANTEE], [PERMISSION_READ]))
    elif acl == "public-read-write":
        grants.append(
            FakeGrant([ALL_USERS_GRANTEE], [PERMISSION_READ, PERMISSION_WRITE])
        )
    elif acl == "authenticated-read":
        grants.append(FakeGrant([AUTHENTICATED_USERS_GRANTEE], [PERMISSION_READ]))
    elif acl == "bucket-owner-read":
        pass  # TODO: bucket owner ACL
    elif acl == "bucket-owner-full-control":
        grants.append(FakeGrant([owner_grantee], [PERMISSION_FULL_CONTROL]))
    elif acl == "aws-exec-read":
        pass  # TODO: bucket owner, EC2 Read
    elif acl == "log-delivery-write":
        grants.append(
            FakeGrant([LOG_DELIVERY_GRANTEE], [PERMISSION_READ_ACP, PERMISSION_WRITE])
        )
    else:
        assert False, "Unknown canned acl: %s" % (acl,)
    return FakeAcl(grants=grants)