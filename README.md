# PVSG Anotation Tool

This repo collects all the code that is used to annotate PVSG dataset.


| ![pvsg.jpg](https://jingkang50.github.io/PVSG/static/images/pipeline.jpg) |
|:--:|
| <b>The PVSG Annotation Pipeline</b>|

</p>
  <p align="center">
  <font size=5><strong>Panoptic Video Scene Graph Generation</strong></font>
    <br>
        <a href="https://jingkang50.github.io/">Jingkang Yang</a>,
        <a href="https://lilydaytoy.github.io/">Wenxuan Peng</a>,
        <a href="https://lxtgh.github.io/">Xiangtai Li</a>,<br>
        <a href="https://scholar.google.com/citations?user=G8DPsoUAAAAJ&amp;hl=zh-CN">Zujin Guo</a>,
        <a href="https://cliangyu.com/"> Liangyu Chen</a>,
        <a href="https://brianboli.com/">Bo Li</a>,
        <a href="https://www.linkedin.com/in/zheng-ma-4201223a/?originalSubdomain=hk">Zheng Ma</a>,<br>
        <a href="https://kaiyangzhou.github.io/">Kaiyang Zhou</a>,
        <a href="https://bmild.github.io/">Wayne Zhang</a>,
        <a href="https://www.mmlab-ntu.com/person/ccloy/">Chen Change Loy</a>,
        <a href="https://liuziwei7.github.io/">Ziwei Liu</a>,
    <br>
  S-Lab, Nanyang Technological University & SenseTime Research
  </p>
</p>

---

## Get Started

**1. Create a New Conda Environment:**
```bash
conda create -n pvsg python=3.8
conda activate myenv
conda install numpy scipy pandas matplotlib ipython jupyter scikit-learn
conda install -c conda-forge opencv
pip install requests beautifulsoup4 lxml
```
Please check `packages_list.txt` to see all the packages required.

**2. Download Annotations From SuperAnnotate:**
```
curl -o zip_files/Task_0205_v18.zip https://files.superannotate.com/xxxxxx
```

**3. Run scripts:**
```
sh run_vidor.sh
```
or
```
sh run_ego.sh
```

Once successful running, your `data` folder would be like:
```
├── aot-benchmark
├── data
│   ├── data_Ego4D_v20_1
│   │   ├── caption_masks
│   │   ├── final_masks
│   │   ├── images
│   │   ├── masks
│   │   ├── sa_Ego4D_v20_1
│   │   ├── tag_videos_Ego4D_v20_1
│   │   ├── class_info.json
│   │   ├── frames.json
│   │   └── results.pickle
│   ├── ...
```


## Citation
If you find our repository useful for your research, please consider citing our paper:
```bibtex
@inproceedings{yang2023pvsg,
    author = {Yang, Jingkang and Peng, Wenxuan and Li, Xiangtai and Guo, Zujin and Chen, Liangyu and Li, Bo and Ma, Zheng and Zhou, Kaiyang and Zhang, Wayne and Loy, Chen Change and Liu, Ziwei},
    title = {Panoptic Video Scene Graph Generation},
    booktitle = {CVPR},
    year = {2023},
}
```

