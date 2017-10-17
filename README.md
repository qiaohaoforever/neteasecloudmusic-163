# neteasecloudmusic-163
Get comments of given playlist and find all the comments of the given user.
这是一个简陋的获取网易云音乐给定歌单的所有评论或找出特定用户在其歌单中的评论的程序。


说明：共有两个.py程序，大体上相同，只有一处不同点————多线程处理的思路上:

    PLAN A：爬取网易云音乐给定歌单或用户的评论(歌曲多线程).py
            思路是先获取给定歌单中的所有歌曲的music_id，然后把music_id进行多线程处理，相当于一次爬取多首音乐的评论，然后再join.
            
            
    PLAN B:爬取网易云音乐给定歌单或用户的评论(评论多线程).py
           思路是先获取给定歌单中的所有歌曲的music_id，然后一次处理一个music_id，其后对该music_id下的评论进行多线程处理，相当把该歌曲的评论分为2            部分，同时爬取，然后再join.
    注：PLAN A爬取速度取决于连续3首歌曲中评论数的最大值，实际上要比PLAN B慢。用我电脑爬取时速度大概在1M评论/h.
