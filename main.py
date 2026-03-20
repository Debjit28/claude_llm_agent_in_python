import argparse
import json
import os
import subprocess

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    messages = [{"role": "user", "content": args.p}]

    while True:
        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=[
                # READ TOOL
                {
                    "type": "function",
                    "function": {
                        "name": "Read",
                        "description": "Read and return the contents of a file",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {"type": "string"}
                            },
                            "required": ["file_path"],
                        },
                    },
                },
                # WRITE TOOL
                {
                    "type": "function",
                    "function": {
                        "name": "Write",
                        "description": "Write content to a file",
                        "parameters": {
                            "type": "object",
                            "required": ["file_path", "content"],
                            "properties": {
                                "file_path": {"type": "string"},
                                "content": {"type": "string"},
                            },
                        },
                    },
                },
                # BASH TOOL
                {
                    "type": "function",
                    "function": {
                        "name": "Bash",
                        "description": "Execute a shell command",
                        "parameters": {
                            "type": "object",
                            "required": ["command"],
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "The command to execute"
                                }
                            },
                        },
                    },
                },
            ],
        )

        response = chat.choices[0].message

        message_dict = {
            "role": response.role,
            "content": response.content,
        }

        if response.tool_calls:
            message_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in response.tool_calls
            ]

        messages.append(message_dict)

        # FINAL RESPONSE
        if not response.tool_calls:
            if response.content:
                print(response.content)
            break

        # EXECUTE TOOLS
        for tc in response.tool_calls:
            args_dict = json.loads(tc.function.arguments)

            if tc.function.name == "Read":
                try:
                    with open(args_dict["file_path"], "r") as f:
                        result = f.read()
                except Exception as e:
                    result = str(e)

            elif tc.function.name == "Write":
                try:
                    with open(args_dict["file_path"], "w") as f:
                        f.write(args_dict["content"])
                    result = "File written successfully"
                except Exception as e:
                    result = str(e)

            elif tc.function.name == "Bash":
                try:
                    completed = subprocess.run(
                        args_dict["command"],
                        shell=True,
                        capture_output=True,
                        text=True,
                    )
                    result = completed.stdout + completed.stderr
                except Exception as e:
                    result = str(e)

            else:
                result = "Unknown tool"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )


if __name__ == "__main__":
    main()