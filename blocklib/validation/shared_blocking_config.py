from typing import Optional, List, Union

from pydantic import BaseModel, Field


class BlockingConfigBase(BaseModel):
    record_id_column: Optional[int] = Field(alias="record-id-col")
    blocking_features: Union[List[int], List[str]] = Field(
        description="Features used for blocking",
        name="blocking-features",
        alias="blocking-features",
    )
    null_sentinel: Optional[str] = Field(
        alias="null-sentinel",
        description="The value that represents a NULL value in the dataset",
        default="",
    )
