import flet as ft
import asyncio
from datetime import datetime, timedelta


async def main(page: ft.Page):
    page.title = "Timer App"
    page.window_width = 300
    page.window_height = 200
    page.window_resizable = False

    timer_duration = timedelta(hours=3)
    end_time = None
    timer_active = False
    flashing = False

    # Set default background color to Alice Blue
    page.bgcolor = "#f0f8ff"

    def format_time(td: timedelta) -> str:
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_current_time():
        current_time.value = datetime.now().strftime("%H:%M")
        page.update()

    def check_special_times():
        now = datetime.now()
        if now.hour in [4, 16] and now.minute == 0 and now.second == 0:
            asyncio.create_task(flash_background())
        else:
            page.bgcolor = "#f0f8ff"
        page.update()

    async def flash_background():
        nonlocal flashing
        flashing = True
        colors = ["#f0f8ff", "red"]
        i = 0
        while flashing:
            page.bgcolor = colors[i % 2]
            i += 1
            page.update()
            await asyncio.sleep(0.5)

    def start_timer():
        nonlocal timer_active, end_time

        if not timer_active:
            future_time = datetime.now() + timer_duration

            if (future_time.hour > 4 and datetime.now().hour < 4) or (
                future_time.hour > 16 and datetime.now().hour < 16
            ):
                warning_text.value = "カフェタッチ間に合わないよ！"
                start_button.text = "Start"
                timer_active = False
            else:
                end_time = future_time
                timer_active = True
                start_button.text = "Pause"
                warning_text.value = ""
        else:
            timer_active = False
            start_button.text = "Start"

        page.update()

    def reset_timer():
        nonlocal timer_active, end_time, timer_duration, flashing

        timer_active = False
        start_button.text = "Start"
        flashing = False
        page.bgcolor = "#f0f8ff"

        next_4_or_16 = datetime.now().replace(minute=0, second=0, microsecond=0)
        if next_4_or_16.hour < 4:
            next_4_or_16 = next_4_or_16.replace(hour=4)
        elif next_4_or_16.hour < 16:
            next_4_or_16 = next_4_or_16.replace(hour=16)
        else:
            next_4_or_16 = next_4_or_16.replace(hour=4) + timedelta(days=1)

        if (next_4_or_16 - datetime.now()) <= timer_duration:
            timer_duration = next_4_or_16 - datetime.now()
            end_time = next_4_or_16
            timer_active = True
            start_button.text = "Pause"
        else:
            timer_duration = timedelta(hours=3)
            end_time = None

        timer_display.value = format_time(timer_duration)
        warning_text.value = ""
        page.update()

    async def update_timer():
        nonlocal timer_active, end_time

        while True:
            if timer_active and end_time:
                remaining = end_time - datetime.now()
                if remaining.total_seconds() <= 0:
                    timer_active = False
                    start_button.text = "Start"
                    timer_display.value = "00:00:00"
                    asyncio.create_task(flash_background())
                else:
                    timer_display.value = format_time(remaining)

            update_current_time()
            check_special_times()
            await asyncio.sleep(1)

    timer_display = ft.Text(
        format_time(timer_duration), size=40, text_align=ft.TextAlign.CENTER
    )

    current_time = ft.Text(
        datetime.now().strftime("%H:%M"),
        size=14,
        text_align=ft.TextAlign.RIGHT,
    )

    warning_text = ft.Text(
        "",
        color=ft.colors.RED,
        size=12,
        text_align=ft.TextAlign.CENTER,
    )

    start_button = ft.ElevatedButton("Start", on_click=lambda _: start_timer())
    reset_button = ft.ElevatedButton("Reset", on_click=lambda _: reset_timer())

    page.add(
        ft.Column(
            [
                ft.Container(timer_display, alignment=ft.alignment.center),
                ft.Row(
                    [warning_text, current_time],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [start_button, reset_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
    )

    asyncio.create_task(update_timer())


ft.app(target=main)
