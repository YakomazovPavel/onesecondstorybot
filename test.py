import ffmpeg


# 63c9aec8-fb76-4a0d-8220-dc7743723c12.mp4
# ffmpeg -loglevel quiet -i input.mp4 output.avi

try:
    (
        ffmpeg.input("./media/test.mp4").output("./media/test.webm").run()
        # .overwrite_output()  # Overwrite output file if it exists
    )

    (
        ffmpeg.input("./media/test.webm")
        .output(
            "./media/test.cut.webm",
            **{"ss": "00:00:00", "to": "00:00:01"},
        )
        .run()
    )
except ffmpeg.Error as e:
    print("FFmpeg Error:", e.stderr.decode("utf8"))
