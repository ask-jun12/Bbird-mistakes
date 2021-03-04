import cv2
import numpy as np

RED = [255,0,0]
WHITE = [255,255,255]

##### main関数 #####
def main(img1, img2):
    # 縦、横を取得
    height1, width1 = get_height_width(img1)
    ### 背景差分法 ###
    mask = bgSubstractor(img1, img2) # マスク1
    ### 間違い部分を赤円で描画するマスクの作成 ###
    # マスク作成
    mask2 = morphology(mask, 8, cv2.MORPH_CLOSE) # マスク2
    mask3 = np.zeros((height1,width1), np.uint8) # マスク3
    # マスク2に対して領域分割
    area_div(mask2, mask3, width1, 0)
    mask3 = morphology(mask3, 8, cv2.MORPH_CLOSE)
    # マスク3に対して領域分割
    area_div(mask3, mask3, width1, 2)
    ### 画像1に作成したマスクを描画する
    mask3 = cv2.cvtColor(mask3, cv2.COLOR_GRAY2BGR) # GRAY画像をBGR変換
    mask3[np.where((mask3 == WHITE).all(axis = 2))] = RED # 白色部分を赤色に変更
    mask3 = cv2.cvtColor(mask3, cv2.COLOR_BGR2RGB) # BGR画像をRGB変換
    mistakes = cv2.addWeighted(src1 = img1, alpha = 0.4, src2 = mask3, beta = 0.6, gamma=0.3) # 画像1にマスクを描画
    cv2.imwrite('after_img/mistakes.png', mistakes)
    print('find_mistakes_success')

##### heightとwidthを取得 #####
def get_height_width(img):
    height, width = img.shape[:2]
    return height, width

##### 背景差分法 #####
def bgSubstractor(img1, img2):
    img1 = cv2.GaussianBlur(img1, (5,5), 0) # ガウシアンフィルタ
    img2 = cv2.GaussianBlur(img2, (5,5), 0) # ガウシアンフィルタ
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG() # 背景差分法
    mask = fgbg.apply(img1)
    mask = fgbg.apply(img2)
    return mask

##### モルフォロジー変換 #####
def morphology(img, n, method):
    kernel = np.ones((n,n), np.uint8) # カーネル
    image_processing = cv2.morphologyEx(img, method, kernel) # モルフォロジー変換
    return image_processing

##### 領域分割 #####
def area_div(img_in, img_out, width1, mode):
    _, thresh = cv2.threshold(img_in, 100, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    n = len(contours)
    # mode （0:円病が、1:長方形描画、2：なし）
    for i in range(n):
        x, y, w, h = cv2.boundingRect(contours[i]) # 座標、幅、高さ
        if mode == 0:
            if x < width1-10: # 切り取り線部分を除去
                cv2.circle(img_out, (x+w//2, y+h//2), 25, (255,255,255), -1) # 円で描画
        elif mode == 1:
            cv2.rectangle(img_out, (x, y), (x+w, y+h), (255,255,255), 2) # 長方形で囲みわかりやすくする