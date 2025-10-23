#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マークダウンファイルのネストされたコードブロックを修正するスクリプト（改良版）
プロンプト例の中にコードブロックが含まれている場合、外側を4つのバッククォートに変更
"""
import sys
import re
from pathlib import Path

# Windows環境でのUnicode出力対応
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def has_nested_code_blocks(content):
    """コードブロック内に別のコードブロック記法があるかチェック"""
    # ```で囲まれた部分の中に、別の```があるかをチェック
    lines = content.split('\n')

    # 行ごとにチェック
    for line in lines:
        # エスケープされていないコードブロック記法を検出
        if line.strip().startswith('```') and not line.strip().startswith('\\`'):
            return True
        # mermaid等の記述も検出
        if '```mermaid' in line or '```sql' in line or '```python' in line or '```typescript' in line or '```[' in line:
            return True

    return False

def fix_markdown_file(filepath):
    """マークダウンファイルを修正"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        lines = content.split('\n')
        result = []
        i = 0
        modified = False

        while i < len(lines):
            line = lines[i]

            # コードブロックの開始を検出（言語指定なしの```）
            if re.match(r'^```\s*$', line.strip()):
                # このコードブロックの内容を取得
                block_start = i
                i += 1
                block_lines = []

                # 終了の```を探す
                while i < len(lines):
                    if re.match(r'^```\s*$', lines[i].strip()):
                        # 終了を見つけた
                        block_end = i
                        block_content = '\n'.join(block_lines)

                        # ブロック内にネストされたコードブロックがあるかチェック
                        if has_nested_code_blocks(block_content):
                            # 外側を4つのバッククォートに変更
                            result.append('````')
                            result.extend(block_lines)
                            result.append('````')
                            modified = True
                        else:
                            # 変更不要
                            result.append(line)
                            result.extend(block_lines)
                            result.append(lines[i])

                        i += 1
                        break
                    else:
                        block_lines.append(lines[i])
                        i += 1
                else:
                    # 終了が見つからなかった（不正な形式）
                    result.append(line)
                    result.extend(block_lines)
            else:
                result.append(line)
                i += 1

        fixed_content = '\n'.join(result)

        # 変更があった場合のみ書き込み
        if fixed_content != original_content and modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True, str(filepath)
        return False, str(filepath)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        import traceback
        traceback.print_exc()
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
    else:
        print("\nNo files needed modification.")

if __name__ == '__main__':
    main()
