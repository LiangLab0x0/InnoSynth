# InnoSynth: 智能文献综述分析系统

<p align="center">
  <img src="docs/images/logo.png" alt="InnoSynth Logo" width="200"/>
</p>

<div align="center">

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GROBID](https://img.shields.io/badge/GROBID-0.7.3-green.svg)](https://github.com/kermitt2/grobid)

</div>

## 📚 项目简介

InnoSynth是一个帮助研究人员快速从批量文献中挖掘创新点的信息。它能够从PDF文档中提取结构化信息，进行深度主题分析，并生成全面的研究报告。

### 🌟 工作流程

- **PDF解析**: 使用GROBID进行精确的PDF文献解析
- **主题分析**: 运用先进的NLP技术进行主题提取和分类
- **多维度分析**: 包括技术创新、研究趋势、挑战和未来方向
- **自动报告生成**: 生成结构化的Markdown报告和JSON数据
- **可视化支持**: 提供研究趋势和主题关联的可视化分析

## 🛠️ ToDO

- ** 需要填的坑...**:
  - 提供研究趋势和主题关联的可视化分析
  - 细化报告中的子内容，并提供可靠的引用格式
  - 更易用的图形界面
  

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Docker (用于运行GROBID服务)
- 8GB+ RAM
- macOS/Linux 操作系统

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/LiangLab0x0/InnoSynth.git
   cd InnoSynth
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   .\venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **安装SpaCy语言模型**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **启动GROBID服务**
   ```bash
   docker pull lfoppiano/grobid:0.7.3
   docker run -d --name grobid -p 8070:8070 lfoppiano/grobid:0.7.3
   ```

### 使用方法

1. **准备文献**
   - 将PDF文件放入 `input` 目录

2. **运行分析**
   ```bash
   python main.py
   ```

3. **查看结果**
   - Markdown报告位于 `output/comprehensive_report.md`
   - JSON数据位于 `output/literature_review.json`

## 📊 输出示例

### 综合报告结构
```
# 纳米马达研究文献综述报告

## 1. 摘要
本报告基于对5篇最新文献的分析，系统总结了纳米马达在生物医学领域的研究进展、技术创新和未来发展方向。

## 2. 研究概述
- 分析文献数量：5篇
- 研究时期：2023-2024
- 研究领域：纳米马达在生物医学领域的应用
- 核心主题：- 智能响应性纳米马达
- 深部组织渗透技术
- 多功能协同治疗
- 精确控制系统

## 3. 关键研究趋势
### 3.1 研究热点
#### 智能响应性设计
- 描述：开发具有多重响应性的纳米马达系统
- 代表性文献：Construction of a matchstick-shaped Au@ZnO@SiO2-ICG Janus nanomotor
- 重要性：提高治疗精准性和效率

#### 深部组织渗透
- 描述：研究纳米马达在复杂生物环境中的运动行为
- 代表性文献：Deep Penetration of Nanolevel Drugs
- 重要性：解决传统药物递送系统的局限性

#### 多功能集成
- 描述：将诊断和治疗功能集成到单一系统
- 代表性文献：Dual-responsive nanomotors for deep tumor penetration
- 重要性：实现诊疗一体化


### 3.2 新兴趋势
- 智能控制系统开发
- 生物安全性评价
- 临床转化研究

## 4. 技术创新
### 4.1 材料创新
#### Janus结构设计
- 描述：开发不对称结构实现定向运动
- 优势：运动方向可控, 功能区域化
- 相关文献：Core@Satellite Janus Nanomotors

#### 响应性材料
- 描述：开发对多种刺激响应的智能材料
- 优势：精确控制, 环境适应性
- 相关文献：Enzyme-Based Mesoporous Nanomotors


### 4.2 方法创新
#### 合成方法
- 描述：开发新型纳米材料合成技术
- 重要性：提高材料性能和可控性

#### 表征技术
- 描述：发展先进表征方法
- 重要性：深入理解材料结构与性能


## 5. 实验结果分析
### 5.1 性能指标
#### 运动性能
- 主要发现：速度可控, 方向可调
- 重要性：实现精确导航

#### 治疗效果
- 主要发现：靶向性好, 疗效显著
- 重要性：提高治疗效果


### 5.2 验证方法
- 体外细胞实验
- 动物模型验证
- 安全性评估

## 6. 技术挑战
### 6.1 当前挑战
#### 技术挑战
- 运动控制精度
- 生物环境适应性
- 长期稳定性

#### 应用挑战
- 生物安全性
- 规模化生产
- 临床转化


### 6.2 潜在解决方案
- 开发新型控制策略
- 优化材料设计
- 建立标准化评价体系

## 7. 未来发展方向
### 7.1 研究方向
#### 智能化提升
- 描述：开发更智能的响应和控制系统
- 潜在影响：提高治疗精准性

#### 临床转化
- 描述：推进临床应用研究
- 潜在影响：实现实际应用


### 7.2 建议
- 加强基础研究
- 推进标准化建设
- 促进产学研合作

## 8. 结论
基于对现有文献的系统分析，纳米马达研究领域展现出快速发展的态势，主要体现在：
1. 智能响应性设计不断创新
2. 深部组织渗透技术取得突破
3. 多功能集成系统日益成熟
4. 临床转化探索逐步深入

建议未来研究重点关注：
1. 提高纳米马达的智能化程度
2. 加强生物安全性评价
3. 探索产业化路径
4. 推进临床转化研究

```



## 🔧 高级配置

### 配置文件
在 `config.py` 中可以调整以下参数：
- GROBID服务地址
- 分析参数
- 输出格式
- 日志级别

### 自定义分析
可以通过修改 `analyzer.py` 来自定义分析逻辑：
- 添加新的分析维度
- 调整主题提取算法
- 自定义报告格式



## 🙏 致谢

感谢以下开源项目：
- [GROBID](https://github.com/kermitt2/grobid)
- [SpaCy](https://spacy.io/)
- [scikit-learn](https://scikit-learn.org/)
