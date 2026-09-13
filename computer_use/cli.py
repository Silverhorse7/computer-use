"""
Command-line interface for computer-use.
"""

import sys
import argparse
from .core import ComputerUseController


def main():
    parser = argparse.ArgumentParser(
        prog="computer-use",
        description="High-Performance Hybrid Computer Use & Browser Automation CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # capture
    p_cap = subparsers.add_parser("capture", help="Capture target window or desktop")
    p_cap.add_argument("output", default="screen.png", nargs="?", help="Output image file path")

    # click
    p_clk = subparsers.add_parser("click", help="Click at (X, Y) coordinates")
    p_clk.add_argument("x", type=int, help="X coordinate")
    p_clk.add_argument("y", type=int, help="Y coordinate")

    # navigate
    p_nav = subparsers.add_parser("navigate", help="Navigate browser to URL")
    p_nav.add_argument("url", help="Target URL")

    # keys
    p_key = subparsers.add_parser("keys", help="Send keys or key combination")
    p_key.add_argument("keys", help="Key string (e.g. '^l', '{ENTER}')")

    # scroll
    p_scrl = subparsers.add_parser("scroll", help="Scroll mouse wheel")
    p_scrl.add_argument("amount", type=int, default=-500, nargs="?", help="Wheel delta")

    # dom-click
    p_domc = subparsers.add_parser("dom-click", help="Click button via DevTools DOM injection")
    p_domc.add_argument("text", help="Button text")

    # dom-radio
    p_domr = subparsers.add_parser("dom-radio", help="Select radio option via DevTools DOM injection")
    p_domr.add_argument("label", help="Label or text substring")

    # dom-fill
    p_domf = subparsers.add_parser("dom-fill", help="Fill input via DevTools DOM injection")
    p_domf.add_argument("label", help="Label or placeholder substring")
    p_domf.add_argument("value", help="Value to set")

    # batch-scan
    p_bscan = subparsers.add_parser("batch-scan", help="Scan image for form fields and buttons")
    p_bscan.add_argument("image", help="Image path to analyze")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cu = ComputerUseController()

    if args.command == "capture":
        res = cu.capture(args.output)
        print(res)
    elif args.command == "click":
        res = cu.click(args.x, args.y)
        print(res)
    elif args.command == "navigate":
        res = cu.navigate(args.url)
        print(res)
    elif args.command == "keys":
        res = cu.press_key(args.keys)
        print(res)
    elif args.command == "scroll":
        res = cu.scroll(args.amount)
        print(res)
    elif args.command == "dom-click":
        res = cu.dom.click_button(args.text)
        print(res)
    elif args.command == "dom-radio":
        res = cu.dom.select_radio(args.label)
        print(res)
    elif args.command == "dom-fill":
        res = cu.dom.fill_input(args.label, args.value)
        print(res)
    elif args.command == "batch-scan":
        boxes = cu.vision.detect_dropdown_boxes(args.image)
        reds = cu.vision.detect_unfilled_red_boxes(args.image)
        btn = cu.vision.detect_primary_button(args.image)
        print(f"Found {len(boxes)} standard fields, {len(reds)} unfilled red fields, primary button: {btn}")


if __name__ == "__main__":
    main()
