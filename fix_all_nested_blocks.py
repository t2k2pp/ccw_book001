#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全てのネストされたコードブロックを検出して修正
"""
import sys
import re
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def fix_file(filepath):
    """ファイル内の全てのネストされたコードブロックを修正"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    lines = content.split('\n')

    # まず全てのコードブロックを検出
    blocks = []
    i = 0
    while i < len(lines):
        match = re.match(r'^(`{3})([a-z]*)\s*$', lines[i])
        if match:
            fence_len = len(match.group(1))
            lang = match.group(2)
            start = i
            i += 1

            # 終了を探す
            while i < len(lines):
                if re.match(r'^`{3}\s*$', lines[i]):
                    end = i
                    block_content = '\n'.join(lines[start+1:end])

                    # ネストされたコードブロックがあるかチェック
                    # ```で始まる行、または\`\`\`を含む行があるか
                    has_nested = bool(re.search(r'```', block_content))

                    blocks.append({
                        'start': start,
                        'end': end,
                        'fence_len': fence_len,
                        'lang': lang,
                        'has_nested': has_nested,
                        'content': block_content
                    })
                    break
                i += 1
        i += 1

    # ネストがあるブロックで3つのバッククォートを使っているものを修正
    needs_fix = [b for b in blocks if b['has_nested'] and b['fence_len'] == 3]

    if not needs_fix:
        return False, filepath

    # 後ろから修正（行番号がずれないように）
    for block in reversed(needs_fix):
        # 開始行を````に変更
        if block['lang']:
            lines[block['start']] = '````' + block['lang']
        else:
            lines[block['start']] = '````'
        # 終了行を````に変更
        lines[block['end']] = '````'

    fixed_content = '\n'.join(lines)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    return True, filepath

def main():
    prompt_guide_dir = Path('prompt_guide')
    if not prompt_guide_dir.exists():
        print("prompt_guide directory not found")
        return

    md_files = list(prompt_guide_dir.rglob('*.md'))
    print(f"Checking {len(md_files)} files...\n")

    fixed = []
    for md_file in sorted(md_files):
        modified, path = fix_file(md_file)
        if modified:
            fixed.append(path)
            print(f"[FIXED] {path}")

    print(f"\n{'='*60}")
    print(f"Fixed {len(fixed)}/{len(md_files)} files")

    if fixed:
        print("\nFixed files:")
        for f in fixed:
            print(f"  - {f}")

if __name__ == '__main__':
    main()
