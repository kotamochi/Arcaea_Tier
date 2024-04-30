import json
import pandas as pd
import random

def create_data(name, level):
    """データを作成する"""
    #指定されたレベルのデータを取得する
    df = pd.read_csv("./data/Arcaea_Music_Data.csv", encoding="utf-8")
    str_level = level

    if level == "11":
        data1 = df[(df["FTR_Level"] == 11) | (df["ETR_Level"] == 11) | (df["BYD_Level"] == 11)]
        data2 = df[(df["FTR_Level"] == 12) | (df["ETR_Level"] == 12) | (df["BYD_Level"] == 12)]
        data = pd.concat([data1, data2])
    else:
        level = float(level)
        data = df[(df["FTR_Level"] == level) | (df["ETR_Level"] == level) | (df["BYD_Level"] == level)]

    #列を追加してデータを保存
    data = data.assign(Point=0, Count=0, Flag=False)
    return data.to_csv(f"./data/temp/{str_level}/{name}_datas.csv", index=False, encoding="utf-8")


def get_music(name, level):
    """ランダムで楽曲を二曲取得する"""
    #データを取得
    df = pd.read_csv(f"./data/temp/{level}/{name}_datas.csv", encoding="utf-8")

    #データを絞る
    df_flag = df[df["Flag"] == False] #まだ選ばれてないものを取得
    #データが一件しか無い時は近いポイントのデータ一つをもう一度比べる
    if len(df_flag) == 1:
        df = df[df["Flag"] == True] #選ばれたものを取得
        df = df.sort_values("Point")
        count = 0
        #このデータと近いpointのデータを取得
        while True:
            df_comp = df[df["Point"] == int(df_flag["Point"].iloc[0]) + count]
            #ないときはpointを+1する
            if df_comp.empty:
                count += 1
            else:
                break
            
        #一曲を取得
        rand = random.randint(0,len(df_comp)-1)
        df_plus = df_comp.iloc[rand]
        df_comp = pd.concat([df_flag, df_plus.to_frame().transpose()])
    else:
        df_flag = df_flag.sort_values("Point")
        df_comp = df_flag[df_flag["Point"] == df_flag.head(1)["Point"].iloc[0]] #最初の行と同じものだけを取得
        #もし一件しかなかった時
        if len(df_comp) == 1:
            #次にポイントが高いもの達の輪に入れる
            df_plus = df_flag[df_flag["Point"] == df_flag.head(2)["Point"].iloc[1]]
            df_comp = pd.concat([df_comp, df_plus])

    #乱数を作成
    choice = []
    rands = []
    for i in range(2):
        while True:
            #重複しない乱数を作成
            rand = random.randint(0,len(df_comp)-1)
            if rand in rands:
                pass
            else:
                rands.append(rand)
                break

        #乱数から選ばれた楽曲を抽出
        hit_music = df_comp.iloc[rand]

        #結果を保存
        title = hit_music["Music_Title"]
        image = hit_music["Image"]
        choice.append([title, image])

    return choice[0][0], choice[0][1], choice[1][0], choice[1][1]


def set_point(name, level, serect_music, non_serect_music, point):
    #データを取得
    df = pd.read_csv(f"./data/temp/{level}/{name}_datas.csv", encoding="utf-8")
    
    #ポイント処理とフラグを立てる
    df = point_flg(df, serect_music, point)
    df = point_flg(df, non_serect_music, 0)
    
    #一周まわったか確認
    df_len = len(df[df["Flag"] == False]) #まだ選ばれてないものを取得
    if df_len == 0:
        df["Flag"] = False #選択されたものを全解除
        
        #データを保存
        df.to_csv(f"./data/temp/{level}/{name}_datas.csv", index=False, encoding="utf-8")
    
        #何週目かを記録する
        with open("./data/user.json", mode="r", encoding="utf-8") as f:
            Users = json.load(f) #自身の情報を取得
        counter = Users[f"{name}"]["counter"] + 1
        Users[f"{name}"]["counter"] = counter

        #保存して次の週に進む
        with open("./data/user.json", mode="w", encoding="utf-8") as f:
            json.dump(Users, f, indent=4, ensure_ascii=False)
        
        #4週回ったら終了する
        if counter == 4:
            #終了処理に移行
            return True
        else:
            #次の週に進む
            return False
    else:
        #データを保存
        df.to_csv(f"./data/temp/{level}/{name}_datas.csv", index=False, encoding="utf-8")
        return False
    

def point_flg(df, music, point):
    #表示済みフラグを付与
    df.loc[df[df["Music_Title"] == music].index, "Flag"] = True
    
    #point処理を行う
    if point != 0:
        now_point = int(df.loc[df[df["Music_Title"] == music].index, "Point"].iloc[0])
        df.loc[df[df["Music_Title"] == music].index, "Point"] = now_point + point #ポイント付与
        df.loc[df[df["Music_Title"] == music].index, "Count"] = 0 #Countリセット
    else:
        count = int(df.loc[df[df["Music_Title"] == music].index, "Count"].iloc[0])
        #同じpointで二回選ばれなかった場合は-1pointする
        if count == 1:
            now_point = int(df.loc[df[df["Music_Title"] == music].index, "Point"].iloc[0])
            df.loc[df[df["Music_Title"] == music].index, "Point"] = now_point -1 #ポイント付与
            df.loc[df[df["Music_Title"] == music].index, "Count"] = 0 #Countリセット
        else: 
            df.loc[df[df["Music_Title"] == music].index, "Count"] = 1 #Count1にする
            
    return df
            

def show_result(name, level):
    #データを取得して並び替える
    df = pd.read_csv(f"./data/temp/{level}/{name}_datas.csv", encoding="utf-8")
    
    #各ポイント事にデータを分ける
    grouped_data = df.groupby('Point')
    rank_list = ["S", "A+", "A", "B+", "B", "C+", "C", "D+", "D", "E+", "E"]
    rank_data = {}
    g_count = 0

    #各ポイントの楽曲を辞書データとして保存
    for point, group in reversed(list(grouped_data)):
        #各ポイント(ランク)のデータをリストに纏めて辞書に変換
        d_count = 0
        d_dic = {}
        for _, data in group.iterrows():
            d_dic[f"{d_count}"] = data["Image"]
            d_count += 1

        rank_data[rank_list[g_count]] = d_dic
        #カウントを進める
        g_count += 1

    return rank_data