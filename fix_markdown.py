#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マークダウンファイルのコードブロック表示崩れを修正するスクリプト
"""
import os
import sys
import re
from pathlib import Path

# Windows環境でのUnicode出力対応
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def fix_markdown_file(filepath):
    """マークダウンファイルを修正"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # バッククォート3つのパターン
        backticks_3 = '```'
        backticks_4 = '````'
        escaped_backticks = r'\`\`\`'

        def replace_code_block(match):
            full_block = match.group(0)
            opening = match.group(1)  # 最初の``` (言語指定含む)
            block_content = match.group(2)

            # ブロック内にエスケープされたコードブロック記法があるかチェック
            if escaped_backticks in block_content:
                # 4つのバッククォートで囲み直す
                new_opening = backticks_4 + opening[3:] if len(opening) > 3 else backticks_4
                return new_opening + '\n' + block_content + backticks_4
            else:
                return full_block

        # 正規表現でコードブロックを検出して置換
        pattern = r'^(```[a-z]*)\n(.*?)\n```'
        fixed_content = re.sub(pattern, replace_code_block, content, flags=re.MULTILINE | re.DOTALL)

        # 変更があった場合のみ書き込み
        if fixed_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True, str(filepath)
        return False, str(filepath)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False, str(filepath)

def main():
    """メイン処理"""
    base_dir = Path('.')
    prompt_guide_dir = base_dir / 'prompt_guide'

    if not prompt_guide_dir.exists():
        print("prompt_guide directory not found")
        return

    # 全てのマークダウンファイルを取得
    md_files = list(prompt_guide_dir.rglob('*.md'))

    print(f"Found {len(md_files)} markdown files\n")

    modified_files = []
    for md_file in md_files:
        modified, filepath = fix_markdown_file(md_file)
        if modified:
            modified_files.append(filepath)
            print(f"[OK] Fixed: {filepath}")

    print(f"\n{'='*60}")
    print(f"Total files modified: {len(modified_files)}/{len(md_files)}")
    if modified_files:
        print("\nModified files:")
        for f in modified_files:
            print(f"  - {f}")

if __name__ == '__main__':
    main()
