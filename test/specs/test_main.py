import pytest
from jsonrpc11base.main import JSONRPCService
from jsonrpc11base.service_description import ServiceDescription

SERVICE_DESCRIPTION = ServiceDescription(
    'Test Service',
    'https://github.com/kbase/kbase-jsonrpc11base/test',
    summary='An test JSON-RPC 1.1 service',
    version='1.0')


def test_service_no_constructor_args():
    with pytest.raises(TypeError) as te:
        JSONRPCService()
    assert "missing 1 required positional argument: 'description'" in str(te.value)


def test_service_simple():
    service = JSONRPCService(SERVICE_DESCRIPTION)
    assert service.service_validation is None
    assert service.validate_params is False
    assert service.validate_result is False


def test_service_simple_nonsensical_args_1():
    with pytest.raises(TypeError) as te:
        JSONRPCService(SERVICE_DESCRIPTION, validate_params=True)
    assert 'May not validate params with no schema_dir provided' in str(te.value)


def test_service_simple_nonsensical_args_2():
    with pytest.raises(TypeError) as te:
        JSONRPCService(SERVICE_DESCRIPTION, validate_result=True)
    assert 'May not validate result with no schema_dir provided' in str(te.value)
