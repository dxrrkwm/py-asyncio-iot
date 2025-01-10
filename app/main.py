import time
import asyncio as aio
from collections.abc import Awaitable

from iot.devices import HueLightDevice, SmartSpeakerDevice, SmartToiletDevice
from iot.message import Message, MessageType
from iot.service import IOTService


async def run_sequence(*functions: Awaitable) -> None:
    for function in functions:
        await function


async def run_parallel(*functions: Awaitable) -> None:
    await aio.gather(*functions)


async def main() -> None:
    # create an IOT service
    service = IOTService()

    # create and register a few devices
    hue_light = HueLightDevice()
    speaker = SmartSpeakerDevice()
    toilet = SmartToiletDevice()
    hue_light_id = service.register_device(hue_light)
    speaker_id = service.register_device(speaker)
    toilet_id = service.register_device(toilet)
    await aio.gather(hue_light_id, speaker_id, toilet_id)

    # create a few programs
    wake_up_program = [
        Message(hue_light_id, MessageType.SWITCH_ON),
        Message(speaker_id, MessageType.SWITCH_ON),
        Message(
            speaker_id,
            MessageType.PLAY_SONG,
            "Rick Astley - Never Gonna Give You Up",
        ),
    ]

    await run_sequence(
        run_parallel(
            service.send_msg(wake_up_program[0]),
            service.send_msg(wake_up_program[1]),
        ),
        service.send_msg(wake_up_program[2]),
    )

    sleep_program = [
        Message(hue_light_id, MessageType.SWITCH_OFF),
        Message(speaker_id, MessageType.SWITCH_OFF),
        Message(toilet_id, MessageType.FLUSH),
        Message(toilet_id, MessageType.CLEAN),
    ]

    await run_sequence(
        run_parallel(
            service.send_msg(sleep_program[0]),
            service.send_msg(sleep_program[1]),
        ),
        run_sequence(
            service.send_msg(sleep_program[2]),
            service.send_msg(sleep_program[3]),
        ),
    )


if __name__ == "__main__":
    start = time.perf_counter()
    aio.run(main())
    end = time.perf_counter()

    print("Elapsed:", end - start)
