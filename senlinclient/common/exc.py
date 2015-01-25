# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import six

from openstack import exceptions as sdkexc
from oslo_serialization import jsonutils

from senlinclient.common.i18n import _

verbose = False


class BaseException(Exception):
    '''An error occurred.'''
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message or self.__class__.__doc__


class CommandError(BaseException):
    '''Invalid usage of CLI.'''


class FileFormatError(BaseException):
    '''Illegal file format detected.'''


class HTTPException(BaseException):
    """Base exception for all HTTP-derived exceptions."""
    code = 'N/A'

    def __init__(self, error=None):
        super(HTTPException, self).__init__(error)
        try:
            self.error = error
            if 'error' not in self.error:
                raise KeyError(_('Key "error" not exists'))
        except KeyError:
            # If key 'error' does not exist, self.message becomes
            # no sense. In this case, we return doc of current
            # exception class instead.
            self.error = {'error': {'message': self.__class__.__doc__}}
        except Exception:
            self.error = {'error':
                          {'message': self.message or self.__class__.__doc__}}

    def __str__(self):
        message = self.error['error'].get('message', 'Internal Error')
        if verbose:
            traceback = self.error['error'].get('traceback', '')
            return (_('ERROR: %(message)s\n%(traceback)s') %
                    {'message': message, 'traceback': traceback})
        else:
            code = self.error['error'].get('code', 'Unknown')
            return _('ERROR(%(code)s): %(message)s') % {'code': code,
                                                        'message': message}


class ClientError(HTTPException):
    pass


class ServerError(HTTPException):
    pass


class HTTPBadRequest(ClientError):
    # 400
    pass


class HTTPUnauthorized(ClientError):
    # 401
    pass


class HTTPForbidden(ClientError):
    # 403
    pass


class HTTPNotFound(ClientError):
    # 404
    pass


class HTTPMethodNotAllowed(ClientError):
    # 405
    pass


class HTTPNotAcceptable(ClientError):
    # 406
    pass


class HTTPProxyAuthenticationRequired(ClientError):
    # 407
    pass


class HTTPRequestTimeout(ClientError):
    # 408
    pass


class HTTPConflict(ClientError):
    # 409
    pass


class HTTPGone(ClientError):
    # 410
    pass


class HTTPLengthRequired(ClientError):
    # 411
    pass


class HTTPPreconditionFailed(ClientError):
    # 412
    pass


class HTTPRequestEntityTooLarge(ClientError):
    # 413
    pass


class HTTPRequestURITooLong(ClientError):
    # 414
    pass


class HTTPUnsupportedMediaType(ClientError):
    # 415
    pass


class HTTPRequestRangeNotSatisfiable(ClientError):
    # 416
    pass


class HTTPExpectationFailed(ClientError):
    # 417
    pass


class HTTPInternalServerError(ServerError):
    # 500
    pass


class HTTPNotImplemented(ServerError):
    # 501
    pass


class HTTPBadGateway(ServerError):
    # 502
    pass


class HTTPServiceUnavailable(ServerError):
    # 503
    pass


class HTTPGatewayTimeout(ServerError):
    # 504
    pass


class HTTPVersionNotSupported(ServerError):
    # 505
    pass


_EXCEPTION_MAP = {
    400: HTTPBadRequest,
    401: HTTPUnauthorized,
    403: HTTPForbidden,
    404: HTTPNotFound,
    405: HTTPMethodNotAllowed,
    406: HTTPNotAcceptable,
    407: HTTPProxyAuthenticationRequired,
    408: HTTPRequestTimeout,
    409: HTTPConflict,
    410: HTTPGone,
    411: HTTPLengthRequired,
    412: HTTPPreconditionFailed,
    413: HTTPRequestEntityTooLarge,
    414: HTTPRequestURITooLong,
    415: HTTPUnsupportedMediaType,
    416: HTTPRequestRangeNotSatisfiable,
    417: HTTPExpectationFailed,
    500: HTTPInternalServerError,
    501: HTTPNotImplemented,
    502: HTTPBadGateway,
    503: HTTPServiceUnavailable,
    504: HTTPGatewayTimeout,
    505: HTTPVersionNotSupported,
}


def parse_exception(exc):
    '''Parse exception code and yield useful information.
    :param details: details of the exception.
    '''
    if isinstance(exc, sdkexc.HttpException):
        record = jsonutils.loads(exc.details)
    elif isinstance(exc, six.string_types):
        record = jsonutils.loads(exc)
    else:
        print(_('Unknown exception: %s') % exc)
        return
    try:
        code = record['error']['code']
    except KeyError as err:
        # Some exception are not caught by SDK, we need to try again
        # The 'code' field may be misplaced
        try:
            code = record['code']
            record['error']['code'] = code
        except KeyError as err:
            print(_('Malformed exception record, missing field "%s"') % err)
            print(_('Original error record: %s') % record)
            return

    if code in _EXCEPTION_MAP:
        inst = _EXCEPTION_MAP.get(code)
        raise inst(record)
    else:
        raise HTTPException(record)
