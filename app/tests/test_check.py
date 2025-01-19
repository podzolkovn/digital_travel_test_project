from time import sleep


async def test_main(async_client):
    response = await async_client.post(
        url="/auth/register",
        json={
            "email": "email@gmail.com",
            "password": "password",
        },
    )
    assert response.status_code == 201
    sleep(15)
