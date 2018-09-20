import base64
import logging
import mimetypes
import os

from apps.eservice.handler import Handler
from apps.helpers import LambdaEventWrapper, Response


class ApiDocHandler(Handler):
    def handle(self, event: LambdaEventWrapper) -> Response:
        logging.info("cwd %s", os.getcwd())
        return serve_from_folder(os.getcwd() + "/api_docs", event.get_path_params().get("asset"))


def serve_from_folder(basepath, asset: str):
    if asset is None:
        return Response.make_response_with_message(404, "Not Found")

    escaped_asset = asset.lstrip("./")

    path_to_asset = basepath + "/" + escaped_asset
    logging.info("serving asset %s", path_to_asset)

    mime_type = mimetypes.guess_type(path_to_asset)[0] or 'text/plain'
    text = False

    if mime_type.startswith('application') or mime_type.startswith("text"):
        text = True

    if os.path.isfile(path_to_asset):
        if not text:
                with open(path_to_asset, "rb") as binary_asset:
                    encoded_string = base64.b64encode(binary_asset.read()).decode("utf-8")
        else:
            with open(path_to_asset, "r") as text_file:
                encoded_string = text_file.read()
    else:
        return Response.make_response_with_message(404, "Not Found")

    return Response.make_response(200, encoded_string, is_base64=not text,
                                  headers={"Content-Type": mime_type})
