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

InnoSynth 是一个强大的智能文献综述分析系统，专门设计用于自动化处理和分析科学文献。它能够从PDF文档中提取结构化信息，进行深度主题分析，并生成全面的研究报告。

### 🌟 主要特性

- **智能PDF解析**: 使用GROBID进行精确的PDF文献解析
- **深度主题分析**: 运用先进的NLP技术进行主题提取和分类
- **多维度分析**: 包括技术创新、研究趋势、挑战和未来方向
- **自动报告生成**: 生成结构化的Markdown报告和JSON数据
- **可视化支持**: 提供研究趋势和主题关联的可视化分析

## 🛠️ 技术架构

- **核心技术**:
  - Python 3.11
  - GROBID 服务
  - SpaCy NLP
  - scikit-learn

- **主要依赖**:
  - requests>=2.31.0
  - numpy>=1.24.3
  - pandas>=2.0.3
  - scikit-learn>=1.3.0
  - spacy>=3.6.0
  - networkx>=3.1
  - matplotlib>=3.7.2
  - seaborn>=0.12.2
  - nltk>=3.8.1
  - gensim>=4.3.1
  - python-dotenv>=1.0.0
  - tqdm>=4.65.0

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
1. 摘要
2. 研究概述
3. 关键研究趋势
4. 技术创新
5. 实验结果分析
6. 技术挑战
7. 未来发展方向
8. 结论
```

### JSON数据结构
```json
{
  "overview": {
    "total_papers": 5,
    "time_period": "2023-2024",
    "research_field": "纳米技术应用"
  },
  "research_trends": [...],
  "technical_innovations": [...],
  "challenges": [...],
  "future_directions": [...]
}
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

## 📈 性能优化

- 使用多进程处理大量PDF文件
- 优化内存使用
- 缓存中间结果
- 支持断点续传

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 团队

- **LiangLab0x0** - *项目负责人* - [GitHub](https://github.com/LiangLab0x0)

## 📞 联系方式

- GitHub Issues: [https://github.com/LiangLab0x0/InnoSynth/issues](https://github.com/LiangLab0x0/InnoSynth/issues)

## 🙏 致谢

感谢以下开源项目：
- [GROBID](https://github.com/kermitt2/grobid)
- [SpaCy](https://spacy.io/)
- [scikit-learn](https://scikit-learn.org/)
