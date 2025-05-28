import httpx
from fastapi import HTTPException
from app.core.config import TMAP_API_KEY

async def get_coords(place: str):
    url = "https://apis.openapi.sk.com/tmap/pois"
    params = {
        "version": "1",
        "format": "json",
        "searchKeyword": place,
        "appKey": TMAP_API_KEY
    }

    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail="POI 검색 실패")
        try:
            data = res.json()
            poi = data["searchPoiInfo"]["pois"]["poi"][0]
            return float(poi["frontLat"]), float(poi["frontLon"])
        except Exception:
            raise HTTPException(status_code=404, detail=f"주소 '{place}'를 찾을 수 없습니다.")

async def get_travel_time(start: tuple, end: tuple):
    url = "https://apis.openapi.sk.com/tmap/routes"
    headers = {
        "appKey": TMAP_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "startX": str(start[1]),
        "startY": str(start[0]),
        "endX": str(end[1]),
        "endY": str(end[0]),
        "reqCoordType": "WGS84GEO",
        "resCoordType": "WGS84GEO",
        "startName": "출발지",
        "endName": "도착지"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=body)
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="경로 검색 실패")

        try:
            data = res.json()
            total_time_sec = data["features"][0]["properties"]["totalTime"]
            return round(total_time_sec / 60)
        except Exception:
            raise HTTPException(status_code=500, detail="소요 시간 파싱 실패")
