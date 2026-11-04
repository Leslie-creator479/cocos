#!/bin/bash
# 새 작업 공간(예약 작업 등)에서 중등 학습지·녹음 도구가 쓰는 부품을 준비한다(2026-11-05). 1~2분, 여러 번 돌려도 같다.
#   bash _tools/mid_sheet/setup_env.sh
set -e
need=""
python3 -c "import kokoro_onnx" 2>/dev/null || need="$need kokoro-onnx==0.6.1"
python3 -c "import soundfile" 2>/dev/null || need="$need soundfile"
python3 -c "import lemminflect" 2>/dev/null || need="$need lemminflect"
[ -n "$need" ] && pip install -q --break-system-packages $need
command -v ffmpeg >/dev/null || (apt-get install -y -qq ffmpeg >/dev/null 2>&1 || echo "ffmpeg 없음: 녹음 줄이기(audio_slim)가 안 됨")
cd "$(dirname "$0")" && python3 -c "from build_audio import ensure_models; ensure_models(); print('녹음 모델 준비됨')"
node -e "require('playwright'); console.log('playwright 준비됨')"
python3 -c "import lemminflect, kokoro_onnx, soundfile; print('파이썬 부품 준비됨')"
