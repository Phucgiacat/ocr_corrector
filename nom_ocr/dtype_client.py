from dataclasses import dataclass
from typing import Optional

@dataclass
class UploadImageReq:
    image: str

@dataclass
class Data:
    file_name: str

@dataclass
class UploadImageRes:
    is_success: bool
    code : str
    message : Optional[str]
    data: Optional[Data]

    @staticmethod
    def dict2obj(dict):
        obj = UploadImageRes(**dict)
        if dict['data'] is not None:
            data = Data(**dict['data'])
            obj.data = data
        else:
            obj.data = None
        return obj
    def json(self):
        return {
            "is_success": self.is_success,
            "code": self.code,
            "message": self.message,
            "data": self.data.__dict__ if self.data else None
        }

@dataclass
class DownloadImageReq:
    file_name: str

@dataclass
class DownloadImageRes:
    file: bytes

@dataclass
class OCRReq:
    ocr_id: 1
    file_name: str

@dataclass
class OCRData:
    result_file_name : str
    result_ocr_text: list
    result_bbox: list

@dataclass
class OCRRes:
    is_success: bool
    code: str
    message: Optional[str]
    data: Optional["OCRData"]

    @staticmethod
    def dict2obj(obj: dict) -> "OCRRes":
        data = obj.get("data", None)
        if isinstance(data, dict):
            data.pop("details", None)
            data = OCRData(**data)
        
        return OCRRes(
            is_success=obj.get("is_success", False),
            code=obj.get("code", ""),
            message = obj.get("message", None),
            data=data
        )