from typing import List
import asyncio
import hashlib
import json
import time
import aiohttp


class AfdianException(Exception):
    pass


class AfdianApiClient:
    def __init__(self, token: str, user_id: str):
        self.token = token
        self.user_id = user_id

    async def send_test_ping(self) -> dict:
        """
        发送一个用以验证sign是否正常的Api

        返回:dict
        """
        return await self.call_api("ping", {"test": "test"})

    async def get_sponsors_by_page(self, page: int):
        """
        获取调用者的赞助者信息

        参数:

        - page 所在的页数

        返回:dict
        """
        return await self.call_api("query-sponsor", {"page": page})

    async def get_all_orders(self) -> List[dict]:
        """
        获取所有的赞助选项

        返回:一个装有所有赞助选项信息的list
        """
        page_num = (await self.get_orders_by_page(1))["total_page"]
        all_sponsers = [
            (await self.get_orders_by_page(i))["list"] for i in range(1, page_num + 1)
        ]
        temp = []
        for i in all_sponsers:
            for f in i:
                temp.append(f)
        return temp

    async def get_all_sponsors(self) -> List[dict]:
        """
        获取所有的赞助者

        返回:一个装有所有赞助者信息的list
        """
        page_num = (await self.get_sponsors_by_page(1))["total_page"]
        all_sponsers = [
            (await self.get_sponsors_by_page(i))["list"] for i in range(1, page_num + 1)
        ]
        temp = []
        for i in all_sponsers:
            for f in i:
                temp.append(f)
        return temp

    async def get_orders_by_page(self, page: int) -> dict:
        """
        获取调用者的赞助订单信息

        参数:

        - page 所在的页数

        返回:dict
        """
        return await self.call_api("query-order", {"page": page})

    async def call_api(self, apiName: str, data: dict) -> dict:
        """
        调用一个爱发电Api

        参数:

        - ApiName api的名称

        - data 传递的数据

        返回:dict
        """
        async with aiohttp.request(
            "POST",
            f"https://afdian.net/api/open/{apiName}",
            data=self.__data_model(data),
        ) as resp:
            json = await resp.json()
            if json["ec"] != 200:
                raise AfdianException(json["em"])
            return json["data"]

    def __data_model(self, params: dict):
        json_params = json.dumps(params)
        ts = time.time()
        data = {
            "user_id": self.user_id,
            "params": json_params,
            "ts": ts,
            "sign": hashlib.md5(
                f"{self.token}params{json_params}ts{ts}user_id{self.user_id}".encode(
                    "utf-8"
                )
            ).hexdigest(),
        }
        return data
