# -*- coding: UTF-8 -*-
import librosa
import soundfile as sf
import os
import numpy as np


error = ""
# 用来写log的多行text控件
log_ctrl = None

#路径
audio_path = ""
vocal_path = ""
music_path = ""


beat_path = ""
click_path = ""

# 音频类型
audio_type = "Song"
audio_types = ["Song", "Vocal", "Music", "Both"]

# 选项
# 是否输出节拍音频
# is_export_click_audio = False

# 节拍处理相关全局变量，这里距离是帧数
music_min_distance = 60
vocal_min_distance = 45
vocal_max_distance = 90
beat_min_distance = 45
beat_max_distance = 120


class Log:
    # 写入
    def append(txt):
        # 判断控件是否为空
        if log_ctrl is None:
            return

        log_ctrl.AppendText(txt+"\n")
    
    # 清空
    def clear():
        # 判断控件是否为空
        if log_ctrl is None:
            return

        log_ctrl.Clear()
        log_ctrl.SetValue("")



# 人声分离
# 返回两个值：
# y_foreground：前景的人声
# y_background：背景的音乐
def vocal_separation(y, sr):
    Log.append("Start vocal separation")
    Log.append("Using filter, it is slow, please wait")
    # And compute the spectrogram magnitude and phase
    S_full, phase = librosa.magphase(librosa.stft(y))

    ###########################################################
    # The wiggly lines above are due to the vocal component.
    # Our goal is to separate them from the accompanying
    # instrumentation.
    #

    # We'll compare frames using cosine similarity, and aggregate similar frames
    # by taking their (per-frequency) median value.
    #
    # To avoid being biased by local continuity, we constrain similar frames to be
    # separated by at least 2 seconds.
    #
    # This suppresses sparse/non-repetetitive deviations from the average spectrum,
    # and works well to discard vocal elements.

    S_filter = librosa.decompose.nn_filter(S_full,
                                        aggregate=np.median,
                                        metric='cosine',
                                        width=int(librosa.time_to_frames(2, sr=sr)))

    # The output of the filter shouldn't be greater than the input
    # if we assume signals are additive.  Taking the pointwise minimum
    # with the input spectrum forces this.
    S_filter = np.minimum(S_full, S_filter)


    Log.append("Setting mask")
    ##############################################
    # The raw filter output can be used as a mask,
    # but it sounds better if we use soft-masking.

    # We can also use a margin to reduce bleed between the vocals and instrumentation masks.
    # Note: the margins need not be equal for foreground and background separation
    margin_i, margin_v = 2, 10
    power = 2

    mask_i = librosa.util.softmask(S_filter,
                                margin_i * (S_full - S_filter),
                                power=power)

    mask_v = librosa.util.softmask(S_full - S_filter,
                                margin_v * S_filter,
                                power=power)

    # Once we have the masks, simply multiply them with the input spectrum
    # to separate the components

    Log.append("Setting vocal")
    S_foreground = mask_v * S_full
    Log.append("Setting music")
    S_background = mask_i * S_full

    ###########################################
    # Recover the foreground audio from the masked spectrogram.
    # To do this, we'll need to re-introduce the phase information
    # that we had previously set aside.

    # 前景是人声，背景是音乐
    Log.append("istft vocal")
    y_foreground = librosa.istft(S_foreground * phase)
    Log.append("istft music")
    y_background = librosa.istft(S_background * phase)

    Log.append("End vocal separation")

    return y_foreground, y_background


# 解析得到节拍，并保存到文件
def gen_beat():
    #重置
    error = ""
    Log.clear()
    Log.append("Start generate beats")


    # 检查音频类型
    Log.append("Audio Type: " + audio_type)
    if audio_type not in audio_types:
        error = "Audio Type is wrong. Current audio type: " + audio_type
        return

    # 检查是否是文件
    if audio_type == audio_types[3]:
        # 检查人声
        if not os.path.isfile(vocal_path):
            error = "Vocal path is not a file"
            return

        # 检查音乐
        if not os.path.isfile(music_path):
            error = "Music path is not a file"
            return

    else:
        # 只需要检查一个音频文件
        if not os.path.isfile(audio_path):
            error = "Audio path is not a file"
            return


    # 获取主文件名
    basename = ""
    beat_path = ""
    click_path = ""
    # 有分开的人声和音乐文件
    if audio_type == audio_types[3]:
        basename = os.path.splitext(vocal_path)[0]
        # 拼接各个路径
        beat_path = basename + "_merged_beats.npy"
        click_path = basename + "_click.wav"
    else:
        basename = os.path.splitext(audio_path)[0]
        beat_path = basename + "_beats.npy"
        click_path = basename + "_click.wav"

    
    # 读取音乐文件, y是数据， sr是采样率
    y = None
    y_vocal = None
    y_music = None
    sr = 0
    sr_vocal = 0
    sr_music = 0
    if audio_type == audio_types[3]:
        # 人声 和 音乐，两个文件
        Log.append("Loading vocal")
        y_vocal, sr_vocal = librosa.load(vocal_path)
        Log.append("Loading music")
        y_music, sr_music = librosa.load(music_path)
    else:
        # 单个声音文件
        Log.append("Loading audio")
        y, sr = librosa.load(audio_path)


    # 初始化
    vocal = None
    music = None
    vocal_beat_frames = None
    music_beat_frames = None

    # 判断音频类型
    # 纯人声
    if audio_type == audio_types[1]:
        vocal = y
    # 纯音乐
    elif audio_type == audio_types[2]:
        music = y
    # 人声和音乐都有
    elif audio_type == audio_types[3]:
        vocal = y_vocal
        music = y_music
    # Song
    else:
        # 人声分离
        Log.append("Separate vocal")
        vocal, music = vocal_separation(y, sr)
        # sf.write(basename+"_vocal.wav", vocal, sr)
        # sf.write(basename+"_music.wav", music, sr)

    # 检测 onset
    # print("detect onset")
    # onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    # onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    # print("onset_frames: ")
    # print(onset_frames)
    # 转为click声音
    # click_onsets = librosa.clicks(frames=onset_frames, sr=sr, length=len(y))
    # 和原声混合
    # 输出
    # sf.write(basename+"_click_onsets.wav", y+click_onsets, sr)


    # 检测 beat
    Log.append("Detecting beats")
    # 纯人声
    if audio_type == audio_types[1]:
        Log.append("Detecting vocal beats")
        tempo, vocal_beat_frames = librosa.beat.beat_track(y=vocal, sr=sr)
    # 纯音乐
    elif audio_type == audio_types[2]:
        Log.append("Detecting music beats")
        tempo, music_beat_frames = librosa.beat.beat_track(y=music, sr=sr)
    # 音乐和人声都有
    elif audio_type == audio_types[3]:
        Log.append("Detecting vocal beats")
        tempo, vocal_beat_frames = librosa.beat.beat_track(y=vocal, sr=sr_vocal)
        Log.append("Detecting music beats")
        tempo, music_beat_frames = librosa.beat.beat_track(y=music, sr=sr_music)
    # 歌曲
    else:
        Log.append("Detecting vocal beats")
        tempo, vocal_beat_frames = librosa.beat.beat_track(y=vocal, sr=sr)
        Log.append("Detecting music beats")
        tempo, music_beat_frames = librosa.beat.beat_track(y=music, sr=sr)



    # print("vocal_beat_frames[0-10]")
    # print(vocal_beat_frames[0:10])

    # print("music_beat_frames[0-10]")
    # print(music_beat_frames[0:10])
    # print('Estimated tempo: {:.2f} beats per minute'.format(tempo))
    # beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    # print("beat_frames: ")
    # print(beat_frames)

    # 不是纯人声，就要处理背景音乐
    if audio_type != audio_types[1]:
    # 背景音乐得到的beat频率过高，必须进行预先过滤
        Log.append("Filter music beats")
        # 过滤距离间隔太短的beat
        merged_music_beats = []
        for i in range(len(music_beat_frames)):
            if len(merged_music_beats) == 0:
                # 第一达到合理距离的数据，直接加入
                if music_beat_frames[i] > music_min_distance:
                    merged_music_beats.append(music_beat_frames[i])
            else:
                # 判断和过滤后的beat中，最后一个beat的距离，是否大于指定距离
                if (music_beat_frames[i] - merged_music_beats[-1]) > music_min_distance:
                    # 添加到列表
                    merged_music_beats.append(music_beat_frames[i])

        # 转为ndarray，覆盖赋值
        music_beat_frames = np.array(merged_music_beats)

    # print("merged_music_beats[0-10]")
    # print(music_beat_frames[0:10])


    # 如果是歌曲，或分开的两种音频，就要整合两种beats列表
    beat_frames = None
    if (audio_type == audio_types[0]) or (audio_type == audio_types[3]):
        # 整合两个beat序列
        # 整合方式是，优先 vocal的。vocal中，长时间没有beat的情况，才使用 music的beat填充

        # 定义要填充的beat列表
        Log.append("Merge beats")
        fill_beats = []
        for i in range(len(vocal_beat_frames)):
            # 判断两个beat之间的距离
            if i == 0:
                # 判断距离
                if vocal_beat_frames[i] > vocal_max_distance:
                    # 开头进行填充
                    for beat in music_beat_frames:
                        if beat<vocal_beat_frames[i]:
                            fill_beats.append(beat)
                        else:
                            break
            else:
                # 判断两个vocal beat的距离
                if (vocal_beat_frames[i] - vocal_beat_frames[i-1]) > vocal_max_distance:
                    # 在这之间填充
                    for beat in music_beat_frames:
                        if (beat > vocal_beat_frames[i-1]) and (beat < vocal_beat_frames[i]):
                            fill_beats.append(beat)
                        elif beat > vocal_beat_frames[i]:
                            # 超过范围不用循环了
                            break

        # print("fill_beats.length: " + str(len(fill_beats)))
    
        # 填充之后，进行合并
        if len(fill_beats) > 0:
            beat_frames = vocal_beat_frames.tolist() + fill_beats
            # 还要排序
            beat_frames.sort()
            # 然后再变回ndarray
            beat_frames = np.array(beat_frames)
        else:
            beat_frames = vocal_beat_frames

    # 纯人声
    elif audio_type == audio_types[1]:
        # 不需要整合
        beat_frames = vocal_beat_frames
    # 纯音乐，也不用整合
    else:
        beat_frames = music_beat_frames


    Log.append("get beat_frames: " + str(len(beat_frames)))

    # print("beat_frames[0-10]")
    # print(beat_frames[0:10])

    # 打印节奏长度
    # print("onset length: " + str(len(onset_frames)))
    # print("beat length: " + str(len(beat_frames)))

    # 显示nparray形状
    # print("onset_frames.shape: ")
    # print(onset_frames.shape)
    # print("beat_frames.shape: ")
    # print(beat_frames.shape)
    
    # 过滤 beat

    # 只保留beat位置，附近有onset的帧
    # crossed_beats = []
    # # 设置判断距离
    # distance = 3

    # for beat in beat_frames:
    #     for onset in onset_frames:
    #         # 检查距离
    #         if abs(beat - onset) < distance:
    #             crossed_beats.append(beat)
    #             break


    # print("crossed_beats length:" + str(len(crossed_beats)))
    # print(crossed_beats)
    # nd_crossed_beats = np.array(crossed_beats)
    # 转为click声音
    # click_beats = librosa.clicks(frames=nd_crossed_beats, sr=sr, length=len(y))
    # # 和原声混合
    # # 输出
    # sf.write(basename+"_crossed_beats.wav", y+click_beats, sr)


    # 按照音量过滤
    # 判断音乐类型，对于混合类型，不进行这个过滤
    rms_beats = []
    if audio_type != audio_types[3]:
        Log.append("Using RMS filter")
        rms = librosa.feature.rms(y=y)

        # 求出rms平均值
        rms_list = rms[0]
        rms_mean = np.mean(rms_list)
        # 求出最大最小值
        rms_max = np.max(rms_list)
        rms_min = np.min(rms_list)
        # print("rms_max: " + str(rms_max))
        # print("rms_mean: " + str(rms_mean))
        # print("rms_min: " + str(rms_min))

        # 按照音量进行过滤
        # 音量过滤，不能按照是否超过，或者低于平均值过滤。
        # 比如，如果用低于平均值过滤，那么可能一整段都音量小，然后副歌整段高音量。于是，前面全是节奏点，后面没有节奏点。
        # 按照音量过滤的方法，是和周围2个节奏点比较，音量的变化幅度，是否足够大。
        # 把音量变化幅度大的点，作为要使用的节奏点，没有波动的点，就消除掉。
        
        # 用列表，保存每2个beat之间的音量变化绝对值
        rms_waves = []
        for i in range(len(beat_frames)):
            if i > 0 and beat_frames[i] < len(rms_list):
                # 获取这一beat和上一beat的rms，并计算rms差异
                rms_wave = abs(rms_list[beat_frames[i]] - rms_list[beat_frames[i-1]])
                # 保存到列表
                rms_waves.append(rms_wave)

        
        # 求出所有差异的平均值，最大值，最小值
        rms_waves_mean = np.mean(rms_waves)
        rms_waves_max = np.max(rms_waves)
        rms_waves_min = np.min(rms_waves)
        # print("rms_waves_mean: " + str(rms_waves_mean))
        # print("rms_waves_max: " + str(rms_waves_max))
        # print("rms_waves_min: " + str(rms_waves_min))

        # 求出平均音量和最小音量的差值
        rms_mean_to_min = abs(rms_mean - rms_min)
        # 计算平均值和最小值的差异
        rms_waves_mean_to_min = abs(rms_waves_mean - rms_waves_min)

        # 定义两个beat之间的最小距离

        # 再次遍历beat，差异大于平均值的，就是需要保留的beat
        rms_beats = []
        for i in range(len(beat_frames)):
            # 第一个满足条件的beat
            if len(rms_beats)==0:
                if beat_frames[i] >= beat_min_distance:
                    rms_beats.append(beat_frames[i])
            else:
                if beat_frames[i] < len(rms_list):
                    # 判断相邻两个beat的音量，是否都小于平均音量 - 最小音量的差值
                    # if (rms_list[beat_frames[i]]< rms_mean_to_min) and (rms_list[beat_frames[i-1]]< rms_mean_to_min):
                    #     # 判断上一个beat是否已经加入
                    #     if beat_frames[i-1] in rms_beats:
                    #         # 判断两个beat的距离是否很短
                    #         if (beat_frames[i] - beat_frames[i-1]) <= distance:
                    #             # 说明这是声音下降时的小波动，直接无视
                    #             continue
                    
                    # 获取这一beat和上一beat的rms，并计算rms差异
                    rms_wave = abs(rms_list[beat_frames[i]] - rms_list[beat_frames[i-1]])

                    # 大于平均值和最小值差异，就加入
                    rate = 1
                    #  不是纯音乐
                    if audio_type != audio_types[2]:
                        # 0.7比1.0适合更多情况
                        rate = 0.7
                    # 纯音乐
                    else:
                        # AI提取的背景音乐，音量特别小。所以，这里要放过更多的beat，而不是排除
                        rate = 0.3

                    if rms_wave >= rms_waves_mean_to_min * rate:
                        rms_beats.append(beat_frames[i])

        Log.append("get rms_beats: " + str(len(rms_beats)))
    
    else:
        # 对于混合类型，不进行这个过滤
        rms_beats = beat_frames.tolist()

    # print("rms_beats length:" + str(len(rms_beats)))
    # print(rms_beats)

    # nd_rms_beats = np.array(rms_beats)

    # # 转为click声音
    # click_beats = librosa.clicks(frames=nd_rms_beats, sr=sr, length=len(y))
    # # 和原声混合
    # # 输出
    # sf.write(basename+"_rms_beats.wav", y+click_beats, sr)




    # 过滤距离间隔太短的beat
    Log.append("Using distance filter")
    merged_beats = []
    for i in range(len(rms_beats)):
        if len(merged_beats) == 0:
            # 第一达到合理距离的数据，直接加入
            if rms_beats[i] > beat_min_distance:
                merged_beats.append(rms_beats[i])
        else:
            # 判断和过滤后的beat中，最后一个beat的距离，是否大于指定距离
            if (rms_beats[i] - merged_beats[-1]) > beat_min_distance:
                # 添加到列表
                merged_beats.append(rms_beats[i])


    Log.append("get merged_beats: " + str(len(merged_beats)))

    Log.append("Fill missing beats")
    # 过滤之后，要根据最大距离，进行二次修复补完
    missing_beats = []
    for i in range(len(merged_beats)):
        if i>0:
            distance = merged_beats[i] - merged_beats[i-1]
            if distance > beat_max_distance:
                # 超过最大距离，要进行补完
                # 在原始beat列表中，找到这两个beat的下标
                index_a = beat_frames.tolist().index(merged_beats[i])
                index_b = beat_frames.tolist().index(merged_beats[i-1])
                # 获取下标中间值
                index_middle = round((index_a+index_b)*0.5)
                # 获取中间beat
                middle_beat = beat_frames[index_middle]
                # 加入补全beat列表
                missing_beats.append(middle_beat)


    Log.append("found missing_beats: " + str(len(missing_beats)))

    # 把补完的beat合并进去
    if len(missing_beats) > 0:
        merged_beats = merged_beats + missing_beats
        # 还要排序
        merged_beats.sort()



    # print("merged_beats length:" + str(len(merged_beats)))
    # print(merged_beats)

    Log.append("final beats: " + str(len(merged_beats)))

    nd_merged_beats = np.array(merged_beats)

    Log.append("Export beat file")
    np.save(beat_path, nd_merged_beats)
    Log.append("Beat file is saved to:")
    Log.append(beat_path)


    # 转为click声音
    # if audio_type != audio_types[3]:
    #     Log.append("Export beat audio")
    #     click_beats = librosa.clicks(frames=nd_merged_beats, sr=sr, length=len(y))
    #     # 和原声混合
    #     # 输出
    #     sf.write(click_path, y+click_beats, sr)


    Log.append("====Done====")

    # 绘图
    # print("plot beats")
    # plt.figure(figsize=(14, 5))
    # librosa.display.waveshow(y, sr=sr)
    # plt.vlines(onset_times, -1, 1, color='r')
    # plt.vlines(beat_times, -1, 1, color='b')
    # plt.ylim(-1, 1)
    # plt.show()

    

    

    
