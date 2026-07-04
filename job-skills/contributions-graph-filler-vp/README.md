<h1 align="center">
  contributions-graph-filler-vp | 缁垮鍒锋紗璁″垝
</h1>

<p align="center">
  GitHub Contribution Graph 鑽掓紶缁垮寲娌荤悊宸ョ▼
</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-orange" alt="license MIT"></a>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="python 3.9+">
  <img src="https://img.shields.io/badge/Codex-Skill-555555" alt="Codex Skill">
  <img src="https://img.shields.io/badge/workflow-Excel--first-brightgreen" alt="Excel first workflow">
</p>

<p align="center">
  绠€浣撲腑鏂?
</p>

---

## 涓轰粈涔堣鍋?

GitHub Contribution Graph 绌鸿崱鑽★紵鐢ㄥ畠灏卞浜嗭紝璧涘崥妞嶆爲閫犳灄璁″垝銆?

<p align="center">
  <img src="assets/contribution-graph-showcase.gif" alt="GitHub Contribution Graph 璧涘崥妞嶆爲閫犳灄璁″垝" width="931">
</p>

GitHub contribution graph 鍙細缁熻宸茬粡杩涘叆 GitHub 浠撳簱銆佷綅浜庨粯璁ゅ垎鏀垨 `gh-pages` 鍒嗘敮銆佸苟涓斾綔鑰呴偖绠辫兘褰掑睘鍒拌处鍙风殑鎻愪氦銆傚彧鍦ㄦ湰鍦?`git commit` 涓嶄細鏀瑰彉璐＄尞鍥撅紱鎻愪氦鍚庝笉 `push`锛屼篃涓嶄細琚?GitHub 缁熻銆?

`contributions-graph-filler-vp` 鎶婅法浠撳簱缁存姢鎿嶄綔鎷嗘垚鍙鏍搞€佸彲鎵ц銆佸彲杩借釜鐨勬祦绋嬨€傚畠涓嶄細闅愬紡瑙﹀彂锛屼篃涓嶄細鐩存帴璺冲埌鎻愪氦锛岃€屾槸鍏堢敓鎴?Excel 瀹℃牳琛紝璁╃敤鎴风‘璁ゆ棩鏈熴€佹彁浜ゆ暟銆佷粨搴撳垎甯冨拰 commit 缁嗗垯銆?

鏍稿績绛栫暐锛?

- **Excel-first**锛氫换浣曟墽琛屽墠蹇呴』鍏堢敓鎴?Excel 瀹℃牳琛紝骞剁瓑寰呯敤鎴锋槑纭‘璁ゃ€?
- **existing-commit-aware**锛氬厛鏌ヨ GitHub 涓婂悓涓€澶╁凡鏈夌殑浣滆€呮彁浜ゆ暟锛屽啀鎵ｅ噺璁″垝鏂板鏁般€?
- **push-then-cleanup**锛氭墽琛岄樁娈靛繀椤诲厛 `push` 鍒?GitHub 榛樿鍒嗘敮骞堕獙璇佽繙绔彲杈撅紝鐒跺悗涓烘瘡涓粨搴撳崟鐙垱寤?cleanup PR 鍒犻櫎鐢熸垚鐨?`docs/` 鏂囦欢銆?

## 宸ヤ綔鍘熺悊

1. 鏄惧紡璋冪敤 `contributions-graph-filler-vp` 鎴?`$contributions-graph-filler-vp`銆?
2. 妫€鏌?`gh`銆丟itHub 鐧诲綍鐘舵€佸拰 API 杩為€氭€с€?
3. 鎵弿璐﹀彿浠撳簱锛岄粯璁ゆ帓闄?fork 鍜?archived 浠撳簱銆?
4. 瑕佹眰 eligible repositories `> 10`銆?
5. 浣跨敤 activity profile 鐢熸垚娲昏穬鏃ュ拰姣忔棩鐩爣鎻愪氦鏁般€?
6. 鏌ヨ褰撳ぉ宸叉湁浣滆€呮彁浜ゆ暟骞舵墸鍑忥細

```python
planned_new_commit_count = max(0, target_commit_count - existing_author_commit_count)
```

7. 杈撳嚭 Excel 瀹℃牳琛ㄣ€?
8. 鐢ㄦ埛纭鍚庢墠鍏佽鎵ц銆?
9. 鍒涘缓璁″垝鍐呮彁浜わ紝`push` 鍒伴粯璁ゅ垎鏀苟楠岃瘉杩滅鍖呭惈鎻愪氦銆?
10. 姣忎釜鍙楀奖鍝嶄粨搴撳崟鐙垱寤?cleanup PR锛屽垹闄ゆ湰娆＄敓鎴愮殑 `docs/` 鏂囦欢銆?

## 鎵ц娴佺▼

```mermaid
flowchart LR
    A["鎵弿 GitHub 浠撳簱"] --> B["绛涢€?eligible repositories"]
    B --> C["鐢熸垚 Excel 瀹℃牳琛?]
    C --> D{"鐢ㄦ埛纭?"}
    D -- "鍚? --> E["鍋滄锛屼笉淇敼浠撳簱"]
    D -- "鏄? --> F["鍒涘缓璁″垝鍐呮彁浜?]
    F --> G["push 鍒伴粯璁ゅ垎鏀?]
    G --> H["楠岃瘉杩滅鍙揪"]
    H --> I["鎸変粨搴撳垱寤?cleanup 鍒嗘敮"]
    I --> J["鍒犻櫎 manifest 璁板綍鐨?docs 鏂囦欢"]
    J --> K["鎵撳紑 cleanup PR"]
```

## 鎵ц妯″紡

| 妯″紡 | 鐢ㄩ€?| 淇敼浠撳簱鏂囦欢 | push 鍒?GitHub | 鍏稿瀷杈撳嚭 |
| --- | --- | --- | --- | --- |
| `plan-only` | 鍙敓鎴?Excel 瀹℃牳璁″垝 | 鍚?| 鍚?| Excel / TSV 瀹℃牳琛?|
| `push-and-cleanup-pr` | 鐢ㄦ埛纭鍚庢墽琛屽畬鏁存祦绋?| 鏄?| 鏄?| pushed commits銆乧leanup PR銆乵anifest |
| `cleanup-pr` | 鍩轰簬宸叉湁 manifest 鍙垱寤烘竻鐞?PR | 鏄紝鍙敼 cleanup 鍒嗘敮 | 鏄紝鍙?push cleanup 鍒嗘敮 | cleanup PR URL銆佸垹闄ゆ枃浠剁粺璁?|

## 蹇€熶笂鎵?

鐢熸垚姣忔棩鑱氬悎瀹℃牳琛細

```powershell
python .\scripts\generate_plan.py `
  --account VectorPeak `
  --start 2026-03-01 `
  --end 2026-04-01 `
  --profile vibe_coding_builder `
  --excel-out plan.xls
```

瀵煎嚭閫?commit 鏄庣粏锛?

```powershell
python .\scripts\generate_plan.py `
  --account VectorPeak `
  --start 2026-03-01 `
  --end 2026-04-01 `
  --granularity commit `
  --excel-out commit-detail.xls `
  --out commit-detail.tsv
```

`--end` 浣跨敤宸﹂棴鍙冲紑璇箟銆傚鏋滆鍖呭惈 `2026-03-31`锛屽簲浼犲叆 `--end 2026-04-01`銆?

## 杈撳嚭鏍煎紡

榛樿 Excel 瀹℃牳琛ㄥ瓧娈碉細

```text
鏃ユ湡 | 鐩爣鎻愪氦鏁?| 宸叉湁浣滆€呮彁浜ゆ暟 | 鏈璁″垝鏂板鏁?| commit 缁嗗垯
```

閫?commit 鏄庣粏瀛楁锛?

```text
date | time | repo | kind | task_type | message | path | summary | target_commit_count | existing_commit_count | planned_new_commit_count
```

璁″垝鑴氭湰鍙礋璐ｇ敓鎴愬鏍告潗鏂欙紝涓嶄細 `commit`銆乣push` 鎴栧垱寤?cleanup PR銆?

Excel 瀹℃牳琛ㄧず渚嬶細

| 鏃ユ湡 | 鐩爣鎻愪氦鏁?| 宸叉湁浣滆€呮彁浜ゆ暟 | 鏈璁″垝鏂板鏁?| commit 缁嗗垯 |
| --- | ---: | ---: | ---: | --- |
| 2026-03-05 | 4 | 1 | 3 | `21:10 KnowFoundry-RAG-Console docs: add retrieval notes`; `22:35 LLM-Wiki analysis: record validation split`; `23:18 OpenSense tests: document smoke test plan` |
| 2026-03-08 | 3 | 0 | 3 | `10:24 carbon-tower-predictor model: add lag feature notes`; `16:40 vectorpeak-blogs docs: add topic notes`; `20:05 kaggle-tabular-forge eval: add baseline checklist` |

## Cleanup PR

鎵ц妯″紡閲囩敤 `push-and-cleanup-pr`锛?

- 鍏堝皢璁″垝鍐呮彁浜ゆ帹閫佸埌鍚勪粨搴撻粯璁ゅ垎鏀€?
- 楠岃瘉姣忔潯鎻愪氦閮借兘浠庤繙绔粯璁ゅ垎鏀闂€?
- 涓烘瘡涓彈褰卞搷浠撳簱鍒涘缓涓€涓?cleanup 鍒嗘敮銆?
- 鍒犻櫎 manifest 璁板綍鐨勭敓鎴愭枃浠躲€?
- 鎻愪氦骞舵帹閫?cleanup 鍒嗘敮銆?
- 涓烘瘡涓粨搴撴墦寮€涓€涓?draft PR銆?

GitHub PR 鍙兘灞炰簬鍗曚釜浠撳簱锛屽洜姝よ法浠撳簱娓呯悊蹇呴』鏄竴浠撳簱涓€涓?PR銆?

甯歌鐢熸垚鐩綍锛?

```text
docs/notes/
docs/testing/
docs/config/
docs/maintenance/
docs/evaluation/
docs/editorial/
docs/experiments/
docs/review/
```

## 鐩綍缁撴瀯

```text
contributions-graph-filler-vp/
|-- SKILL.md
|-- README.md
|-- LICENSE
|-- agents/
|   `-- openai.yaml
|-- references/
|   `-- activity-profiles.md
`-- scripts/
    `-- generate_plan.py
```

## 娉ㄦ剰浜嬮」

- 鍙厑璁告樉寮忚Е鍙戯紝涓嶄粠鏅€?GitHub銆乧ommit銆佽础鐚浘鎴栫豢澧欒璁轰腑闅愬紡鍚姩銆?
- 鐢熸垚 Excel 鍚庡繀椤荤瓑寰呯敤鎴风‘璁わ紝涓嶈兘鐩存帴杩涘叆鎵ц銆?
- 榛樿娴佺▼涓嶄娇鐢?`git revert` 鍋氭挙鍥烇紝涔熶笉浣跨敤 `reset --hard + force push`銆?
- 鍘嗗彶閲嶅啓鍙綔涓轰簨鏁呮仮澶嶇粡楠岋紝涓嶄綔涓哄父瑙勬墽琛岃矾寰勩€?
- 涓嶅垱寤虹┖ commit銆佷笉鍐欎复鏃跺崰浣嶄唬鐮併€佷笉鐢熸垚鎻愪氦鍚庡啀鍒犻櫎鐨勫亣鍐呭銆?
- 濡傛灉鏈湴宸叉湁鍚屼粨搴?dirty worktree锛屽繀椤诲厛璇㈤棶鐢ㄦ埛鏄惁浣跨敤闅旂 clone銆?

## FAQ

### 涓轰粈涔堟湰鍦?commit 涓嶇畻璐＄尞锛?

GitHub 璐＄尞鍥剧粺璁＄殑鏄?GitHub 鏈嶅姟鍣ㄤ笂鍙綊灞炲埌璐﹀彿鐨勮础鐚簨浠躲€傚彧鍦ㄦ湰鍦版墽琛?`git commit`锛孏itHub 涓嶇煡閬撹繖鏉℃彁浜ゅ瓨鍦紝鎵€浠ヤ笉浼氳鍏ヨ础鐚浘銆?

### 涓轰粈涔堝繀椤?push锛?

commit 闇€瑕佽繘鍏?GitHub 浠撳簱锛屽苟涓旈€氬父闇€瑕佷綅浜庨粯璁ゅ垎鏀垨 `gh-pages` 鍒嗘敮锛屾墠鍙兘琚?contribution graph 缁熻銆傚彧 commit 涓?push锛屼笉浼氳 GitHub 缁熻銆?

### 涓轰粈涔?cleanup PR 鏄竴浠撳簱涓€涓紵

GitHub PR 鍙兘灞炰簬涓€涓粨搴擄紝涓嶈兘璺ㄥ涓粨搴撴彁浜ゅ悓涓€涓?PR銆傝法浠撳簱鎵ц鏃讹紝姣忎釜鍙楀奖鍝嶄粨搴撻兘闇€瑕佸崟鐙殑 cleanup 鍒嗘敮鍜?cleanup PR銆?

### GitHub 璐＄尞鍥句负浠€涔堝彲鑳藉欢杩熷埛鏂帮紵

璐＄尞鍥句笉鏄瘡娆?push 鍚庨兘绔嬪嵆鍚屾閲嶇畻銆侴itHub 浼氬紓姝ュ鐞嗘彁浜ゅ綊灞炪€佸垎鏀彲杈炬€с€侀偖绠卞尮閰嶃€丳R/issue 绛夎础鐚簨浠讹紝鍥犳椤甸潰鏄剧ず鍙兘瀛樺湪缂撳瓨鎴栧欢杩熴€?
