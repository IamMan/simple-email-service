import logging

import apps.emailservice as eservice


def assemble_request(path, path_params=None, query_params=None, method='GET'):
    path_params = path_params or {}
    query_params = query_params or {}

    return {
        "httpMethod": method,
        "resource": path,
        "pathParameters": path_params,
        "queryStringParameters": query_params
    }


def test_api_doc():
    res = eservice.handler(
        assemble_request(
            "/api-docs/{asset}",
            path_params=dict(
                asset="swagger.yml"
            )
        )
    )

    logging.info(res.get("headers"))
    code = res.get("statusCode")
    assert code is not None and code == 200
    import json
    json.dumps(res)
    assert not res.get("isBase64Encoded")
    logging.info(res)
