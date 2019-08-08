在扩充数据之前对训练bbox标注做分类。

分为四类：

1. unvalid_bbox.txt 无效文本框，包括‘###’标注和尺寸过小文本（根据具体任务自行设定）
2. long_str.txt 长文本bbox
3. vertical_bbox.txt 竖直文本框
4. normal_bbox.txt 正常水平文本框

