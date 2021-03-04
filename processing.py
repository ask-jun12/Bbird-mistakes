import cv2
import statistics

##### main関数 #####
def main(i):
    if i == 1:
        ### 画像の読み込み ###
        img = cv2.imread('before_img/img1.png')
        # 縦、横を取得
        height, width = get_height_width(img)
        ### 前処理 ###
        # 前処理（2分割）
        img1 = img[0:height, 0:width//2] # 画像1
        img2 = img[0:height, width//2:width] # 画像2
        # 前処理（余白除去）
        img1, img2 = delete_margin(img, img1, img2)
    elif i == 2:
        img1 = cv2.imread('before_img/img1.png') # 画像1
        img2 = cv2.imread('before_img/img2.png') # 画像2
    cv2.imwrite('after_img/img1.png', img1)
    cv2.imwrite('after_img/img2.png', img2)
    print('processing_success')

##### heightとwidthを取得 #####
def get_height_width(img):
    height, width = img.shape[:2]
    return height, width

##### 前処理（余白除去） #####
def delete_margin(img, img1, img2):
    # AKAZEの生成
    akaze = cv2.AKAZE_create()

    # 特徴量の検出と特徴量ベクトルの計算
    kp1, des1 = akaze.detectAndCompute(img1, None)
    kp2, des2 = akaze.detectAndCompute(img2, None)

    # Brute-Force Matcher生成
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # 特徴量ベクトル同士をBrute-Forceでマッチング
    matches = bf.match(des1, des2)
    matches = sorted(matches, key = lambda x:x.distance) # distanceをkeyとしてソート

    # 類似度が高い上位10個の特徴点を抽出、空白と分割すべきサイズを取得
    img1_pt = [list(map(int, kp1[m.queryIdx].pt)) for m in matches] # 画像1の特徴点の座標
    img2_pt = [list(map(int, kp2[m.trainIdx].pt)) for m in matches] # 画像2の特徴点の座標
    blank_width = [] # 特徴点のx座標の差
    blank_height = [] # 特徴点のy座標の差

    # for文で20個程の余白の幅（特徴点の差）を格納する。
    # 特徴点の座標を取得、x座標の差の最頻値（mode関数）を余白部分の幅とする。
    for i in range(21):
        blank_width.append(img1_pt[i][0]-img2_pt[i][0])
        blank_height.append(img1_pt[i][1]-img2_pt[i][1])
    mode_blank_width = statistics.mode(blank_width) # widthの余白
    mode_blank_height = statistics.mode(blank_height) # heightの余白

    height, width = get_height_width(img)
    # 画像１
    img1 = img[mode_blank_height:height-mode_blank_height, mode_blank_width:width//2]
    # 画像２
    img2 = img[mode_blank_height:height-mode_blank_height, width//2:width-mode_blank_width]

    ### テンプレートマッチングによるズレの修正 ###
    mis_h, mis_w = template_matching(img1, img2)
    img2 = img[mode_blank_height+mis_h:height-mode_blank_height+mis_h, width//2+mis_w:width-mode_blank_width+mis_w]
    return img1, img2

##### テンプレートマッチング #####
def template_matching(img1, img2):
    n = 80 # テンプレートの（0,0）
    template = img2[n:100+n, n:100+n]
    result = cv2.matchTemplate(img1, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    mis_h = n - max_loc[1] # 縦のズレ
    mis_w = n - max_loc[0] # 横のズレ
    return mis_h, mis_w