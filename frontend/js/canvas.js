/**
 * Canvas手書き入力処理
 */

/**
 * Canvasの初期化
 * @param {string} canvasId - Canvas要素のID
 * @param {number} size - Canvasサイズ（ピクセル）
 * @param {Function} onDrawEnd - 描画終了時のコールバック関数（オプション）
 * @returns {Object} { canvas, ctx, clear, getImageData }
 */
function initCanvas(canvasId, size = 280, onDrawEnd = null) {
  const canvas = document.getElementById(canvasId);

  if (!canvas) {
    console.error(`Canvas element not found: ${canvasId}`);
    alert('かきこみエリアのじゅんびにしっぱいしました。\nページをリロードしてください。');
    throw new Error(`Canvas element ${canvasId} not found`);
  }

  const ctx = canvas.getContext('2d');

  if (!ctx) {
    console.error(`Failed to get 2D context for canvas: ${canvasId}`);
    alert('かきこみエリアのじゅんびにしっぱいしました。\nブラウザをこうしんしてください。');
    throw new Error(`Failed to get 2D context for ${canvasId}`);
  }

  canvas.width = size;
  canvas.height = size;

  // 背景を白に設定
  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, size, size);

  // 描画設定
  ctx.strokeStyle = 'black';
  ctx.lineWidth = 20;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  let isDrawing = false;
  let lastX = 0;
  let lastY = 0;
  let debounceTimer = null; // デバウンス用タイマー

  // マウス/タッチイベント
  canvas.addEventListener('mousedown', startDrawing);
  canvas.addEventListener('mousemove', draw);
  canvas.addEventListener('mouseup', stopDrawing);
  canvas.addEventListener('mouseout', stopDrawing);

  canvas.addEventListener('touchstart', handleTouchStart);
  canvas.addEventListener('touchmove', handleTouchMove);
  canvas.addEventListener('touchend', stopDrawing);

  function startDrawing(e) {
    isDrawing = true;
    [lastX, lastY] = [e.offsetX, e.offsetY];
  }

  function draw(e) {
    if (!isDrawing) return;

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.stroke();

    [lastX, lastY] = [e.offsetX, e.offsetY];
  }

  function stopDrawing() {
    if (!isDrawing) return;
    isDrawing = false;

    // コールバックがある場合、デバウンス処理で呼び出す
    if (onDrawEnd) {
      // 既存のタイマーをクリア
      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }

      // 300ms後にコールバックを実行
      debounceTimer = setTimeout(() => {
        onDrawEnd();
      }, 300);
    }
  }

  function handleTouchStart(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    lastX = touch.clientX - rect.left;
    lastY = touch.clientY - rect.top;
    isDrawing = true;
  }

  function handleTouchMove(e) {
    if (!isDrawing) return;
    e.preventDefault();

    const touch = e.touches[0];
    const rect = canvas.getBoundingClientRect();
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.stroke();

    [lastX, lastY] = [x, y];
  }

  // Canvas をクリア
  function clear() {
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, size, size);

    // デバウンスタイマーをクリア
    if (debounceTimer) {
      clearTimeout(debounceTimer);
      debounceTimer = null;
    }
  }

  // 28x28にリサイズして正規化したデータを取得
  function getImageData() {
    // 一時Canvasで28x28にリサイズ
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = 28;
    tempCanvas.height = 28;
    const tempCtx = tempCanvas.getContext('2d');

    tempCtx.drawImage(canvas, 0, 0, 28, 28);
    const imageData = tempCtx.getImageData(0, 0, 28, 28);

    // グレースケール化・正規化
    const normalized = new Float32Array(28 * 28);
    for (let i = 0; i < 28 * 28; i++) {
      // RGBAのうちR値を使用（白黒なので同じ）
      const pixelValue = imageData.data[i * 4];
      // 0-255を0-1に正規化（背景白→0, 線黒→1に反転）
      normalized[i] = 1 - (pixelValue / 255);
    }

    return normalized;
  }

  return { canvas, ctx, clear, getImageData };
}

/**
 * Float32Array画像データをCanvasに表示
 * @param {string} canvasId - Canvas要素のID
 * @param {Float32Array} imageData - 28x28画像データ
 * @param {number} displaySize - 表示サイズ（ピクセル）
 * @returns {boolean} 成功した場合はtrue、失敗した場合はfalse
 */
function displayImageOnCanvas(canvasId, imageData, displaySize = 56) {
  // 入力検証: imageDataの存在チェック
  if (!imageData || imageData.length === 0) {
    console.error(`displayImageOnCanvas: Invalid imageData for ${canvasId}`, {
      imageData: imageData,
      length: imageData ? imageData.length : 'undefined'
    });
    return false;
  }

  // 入力検証: imageDataのサイズチェック
  if (imageData.length !== 28 * 28) {
    console.error(`displayImageOnCanvas: Invalid imageData size for ${canvasId}`, {
      expected: 28 * 28,
      actual: imageData.length
    });
    return false;
  }

  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    console.error(`Canvas element not found: ${canvasId}`);
    return false;
  }

  // 新規: データ内容の検証
  const hasNaN = Array.from(imageData).some(v => isNaN(v));
  if (hasNaN) {
    console.error(`displayImageOnCanvas: imageData contains NaN for ${canvasId}`);
    return false;
  }

  // 新規: すべて同じ値かチェック（デバッグ用）
  const allSame = Array.from(imageData).every(v => v === imageData[0]);
  if (allSame) {
    console.warn(`displayImageOnCanvas: All pixels have same value (${imageData[0]}) for ${canvasId}`);
  }

  const ctx = canvas.getContext('2d');

  canvas.width = displaySize;
  canvas.height = displaySize;

  // 28x28の一時Canvas
  const tempCanvas = document.createElement('canvas');
  tempCanvas.width = 28;
  tempCanvas.height = 28;
  const tempCtx = tempCanvas.getContext('2d');

  const imgData = tempCtx.createImageData(28, 28);

  for (let i = 0; i < 28 * 28; i++) {
    const value = Math.floor((1 - imageData[i]) * 255);
    imgData.data[i * 4] = value;     // R
    imgData.data[i * 4 + 1] = value; // G
    imgData.data[i * 4 + 2] = value; // B
    imgData.data[i * 4 + 3] = 255;   // A
  }

  tempCtx.putImageData(imgData, 0, 0);

  // 拡大して表示
  ctx.drawImage(tempCanvas, 0, 0, displaySize, displaySize);

  return true; // 成功
}
