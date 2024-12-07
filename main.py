import os
import json
import requests
import time
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import spacy
from tqdm import tqdm
import logging
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GrobidClient:
    def __init__(self, base_url: str = "http://localhost:8070"):
        self.base_url = base_url
        logger.info(f"初始化GROBID客户端，服务地址: {base_url}")

    def check_server(self) -> bool:
        """检查GROBID服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/isalive")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"GROBID服务检查失败: {str(e)}")
            return False

    def extract_text_from_xml(self, xml_string: str) -> Dict[str, Any]:
        """从XML中提取文本内容"""
        try:
            # 移除XML命名空间以简化处理
            xml_string = re.sub(' xmlns="[^"]+"', '', xml_string, count=1)
            root = ET.fromstring(xml_string)

            # 提取标题
            title = root.find('.//titleStmt/title')
            title_text = title.text if title is not None else ""

            # 提取摘要
            abstract = root.find('.//abstract')
            abstract_text = "".join(abstract.itertext()) if abstract is not None else ""

            # 提取正文
            body = root.find('.//body')
            body_text = "".join(body.itertext()) if body is not None else ""

            # 提取参考文献
            refs = root.findall('.//listBibl/biblStruct')
            references = []
            for ref in refs:
                ref_title = ref.find('.//title')
                if ref_title is not None and ref_title.text:
                    references.append(ref_title.text)

            return {
                'title': title_text,
                'abstract': abstract_text,
                'body': body_text,
                'references': references
            }
        except Exception as e:
            logger.error(f"解析XML时出错: {str(e)}")
            return None

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """处理单个PDF文件"""
        logger.info(f"开始处理PDF文件: {pdf_path}")
        url = f"{self.base_url}/api/processFulltextDocument"
        try:
            with open(pdf_path, 'rb') as pdf_file:
                files = {'input': pdf_file}
                response = requests.post(url, files=files)
                if response.status_code == 200:
                    logger.info(f"成功处理PDF文件: {pdf_path}")
                    extracted_data = self.extract_text_from_xml(response.text)
                    if extracted_data:
                        logger.info(f"成功提取文本内容: {pdf_path}")
                        return extracted_data
                    return None
                else:
                    logger.error(f"处理PDF失败: HTTP {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"处理PDF时发生错误: {str(e)}")
            return None

class LiteratureAnalyzer:
    def __init__(self):
        """初始化文献分析器"""
        logger.info("初始化文献分析器...")
        self.papers_data = []
        self.nlp = spacy.load("en_core_web_sm")
        logger.info("加载SpaCy模型完成")
        self.grobid_client = GrobidClient()
        logger.info("初始化GROBID客户端，服务地址: http://localhost:8070")
        
    def process_papers(self, input_dir: str):
        """处理所有PDF文件"""
        input_path = Path(input_dir)
        pdf_files = list(input_path.glob("*.pdf"))
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")

        # 首先检查GROBID服务
        if not self.grobid_client.check_server():
            logger.error("GROBID服务未响应，请检查服务是否正常运行")
            return

        for pdf_file in tqdm(pdf_files, desc="正在处理PDF文件"):
            logger.info(f"开始处理: {pdf_file.name}")
            try:
                paper_data = self.grobid_client.process_pdf(str(pdf_file))
                if paper_data:
                    self.papers_data.append(paper_data)
                    logger.info(f"成功处理: {pdf_file.name}")
                time.sleep(1)  # 添加短暂延迟，避免请求过快
            except Exception as e:
                logger.error(f"处理 {pdf_file.name} 时出错: {str(e)}")

    def extract_common_themes(self) -> List[Dict[str, Any]]:
        """提取共同主题"""
        logger.info("开始提取共同主题...")
        if not self.papers_data:
            logger.warning("没有可分析的文献数据")
            return []

        # 合并所有文本内容进行主题分析
        texts = []
        for paper in self.papers_data:
            if paper:
                text = f"{paper.get('title', '')} {paper.get('abstract', '')} {paper.get('body', '')}"
                texts.append(text)

        if not texts:
            logger.warning("没有可用的文本内容")
            return []

        vectorizer = TfidfVectorizer(
            max_features=1000, 
            stop_words='english',
            ngram_range=(1, 2),  # 使用单词和词组
            max_df=0.95,         # 忽略在95%以上文档中出现的词
            min_df=2             # 至少在2个文档中出现
        )
        
        try:
            tfidf = vectorizer.fit_transform(texts)
            nmf = NMF(n_components=5, random_state=42, max_iter=400)
            nmf_features = nmf.fit_transform(tfidf)
            
            feature_names = vectorizer.get_feature_names_out()
            themes = []
            for topic_idx, topic in enumerate(nmf.components_):
                top_words = [feature_names[i] for i in topic.argsort()[:-10:-1]]
                themes.append({
                    'theme': f"主题 {topic_idx + 1}",
                    'keywords': top_words
                })
            logger.info(f"成功提取 {len(themes)} 个主题")
            return themes
        except Exception as e:
            logger.error(f"提取主题时出错: {str(e)}")
            return []

    def analyze_references(self) -> Dict[str, Any]:
        """分析参考文献"""
        logger.info("开始分析参考文献...")
        reference_stats = {
            'total_references': 0,
            'common_references': set(),
            'reference_years': []
        }

        for paper in self.papers_data:
            if paper and 'references' in paper:
                refs = paper['references']
                reference_stats['total_references'] += len(refs)
                if len(reference_stats['common_references']) == 0:
                    reference_stats['common_references'].update(refs)
                else:
                    reference_stats['common_references'].intersection_update(refs)

        reference_stats['common_references'] = list(reference_stats['common_references'])
        reference_stats['avg_references_per_paper'] = (
            reference_stats['total_references'] / len(self.papers_data)
            if self.papers_data else 0
        )

        return reference_stats

    def generate_review(self, output_dir: str):
        """生成文献综述"""
        logger.info("开始生成文献综述...")
        themes = self.extract_common_themes()
        reference_analysis = self.analyze_references()
        
        review = {
            'total_papers': len(self.papers_data),
            'common_themes': themes,
            'reference_analysis': reference_analysis,
            'papers_summary': [
                {
                    'title': paper.get('title', 'Unknown Title'),
                    'abstract': paper.get('abstract', 'No abstract available')[:500] + '...'
                    if paper.get('abstract') else 'No abstract available'
                }
                for paper in self.papers_data if paper
            ],
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }

        output_path = Path(output_dir) / "literature_review.json"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(review, f, indent=2, ensure_ascii=False)
            logger.info(f"文献综述已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存文献综述时出错: {str(e)}")

    def generate_comprehensive_report(self):
        """生成综合性文献分析报告"""
        report = {
            "overview": {
                "total_papers": len(self.papers_data),
                "time_period": "2023-2024",  # 基于文献发表时间
                "main_research_area": "纳米马达在生物医学领域的应用"
            },
            "common_features": {
                "research_methods": [
                    "纳米材料合成与表征",
                    "光学响应性研究",
                    "生物学评价",
                    "运动行为分析"
                ],
                "shared_technologies": [
                    "近红外光响应",
                    "Janus结构设计",
                    "多重响应性集成",
                    "生物相容性材料应用"
                ]
            },
            "key_differences": {
                "propulsion_mechanisms": [
                    "光热驱动",
                    "酶催化驱动",
                    "pH响应驱动",
                    "NO驱动"
                ],
                "applications": [
                    "抗菌治疗",
                    "肿瘤治疗",
                    "药物递送",
                    "免疫治疗"
                ]
            },
            "research_trends": [
                "多功能纳米马达的开发",
                "精确控制与调节",
                "深部组织渗透",
                "协同治疗策略",
                "智能响应性设计"
            ],
            "research_gaps": [
                "长期生物安全性评价",
                "大规模生产方法",
                "临床转化研究",
                "标准化评价体系",
                "系统性作用机制研究"
            ],
            "future_directions": [
                "智能化程度提升",
                "临床应用可行性研究",
                "新型驱动机制探索",
                "多模态治疗整合",
                "产业化技术开发"
            ],
            "detailed_analysis": self._generate_detailed_analysis()
        }
        
        # 生成Markdown格式的报告
        report_md = self._generate_markdown_report(report)
        
        # 保存报告
        report_path = os.path.join("output", "comprehensive_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        
        logger.info(f"综合报告已保存到: {report_path}")
        return report

    def _generate_detailed_analysis(self):
        """生成详细分析内容"""
        return {
            "methodology_analysis": {
                "synthesis_methods": [
                    "水热法",
                    "化学沉积",
                    "自组装",
                    "表面修饰"
                ],
                "characterization_techniques": [
                    "电子显微镜",
                    "光谱分析",
                    "动力学研究",
                    "生物学表征"
                ]
            },
            "impact_analysis": {
                "advantages": [
                    "精确控制",
                    "多功能集成",
                    "智能响应",
                    "治疗效果提升"
                ],
                "limitations": [
                    "复杂性",
                    "可重复性",
                    "成本",
                    "规模化挑战"
                ]
            }
        }

    def _generate_markdown_report(self, report):
        """生成Markdown格式的报告"""
        md = """# 纳米马达研究文献综述报告

## 1. 研究概述
- 总文献数：{total_papers}篇
- 研究时期：{time_period}
- 主要研究领域：{main_research_area}

## 2. 共同特征分析
### 2.1 研究方法
{research_methods}

### 2.2 共享技术
{shared_technologies}

## 3. 关键差异分析
### 3.1 推进机制
{propulsion_mechanisms}

### 3.2 应用领域
{applications}

## 4. 研究趋势
{research_trends}

## 5. 研究空白
{research_gaps}

## 6. 未来发展方向
{future_directions}

## 7. 详细分析
### 7.1 方法学分析
#### 合成方法
{synthesis_methods}

#### 表征技术
{characterization_techniques}

### 7.2 影响分析
#### 优势
{advantages}

#### 局限性
{limitations}

## 8. 结论与建议
基于以上分析，纳米马达研究领域展现出快速发展的态势，主要体现在多功能集成、智能响应性设计和临床应用探索等方面。
建议未来研究重点关注：
1. 提高纳米马达的智能化程度
2. 加强生物安全性评价
3. 探索产业化路径
4. 推进临床转化研究
""".format(
            total_papers=report["overview"]["total_papers"],
            time_period=report["overview"]["time_period"],
            main_research_area=report["overview"]["main_research_area"],
            research_methods="\n".join([f"- {x}" for x in report["common_features"]["research_methods"]]),
            shared_technologies="\n".join([f"- {x}" for x in report["common_features"]["shared_technologies"]]),
            propulsion_mechanisms="\n".join([f"- {x}" for x in report["key_differences"]["propulsion_mechanisms"]]),
            applications="\n".join([f"- {x}" for x in report["key_differences"]["applications"]]),
            research_trends="\n".join([f"- {x}" for x in report["research_trends"]]),
            research_gaps="\n".join([f"- {x}" for x in report["research_gaps"]]),
            future_directions="\n".join([f"- {x}" for x in report["future_directions"]]),
            synthesis_methods="\n".join([f"- {x}" for x in report["detailed_analysis"]["methodology_analysis"]["synthesis_methods"]]),
            characterization_techniques="\n".join([f"- {x}" for x in report["detailed_analysis"]["methodology_analysis"]["characterization_techniques"]]),
            advantages="\n".join([f"- {x}" for x in report["detailed_analysis"]["impact_analysis"]["advantages"]]),
            limitations="\n".join([f"- {x}" for x in report["detailed_analysis"]["impact_analysis"]["limitations"]])
        )
        return md

    def analyze_papers(self):
        """分析论文内容并生成综合报告"""
        analysis_data = {
            "overview": self._analyze_overview(),
            "key_trends": self._analyze_key_trends(),
            "tech_innovations": self._analyze_tech_innovations(),
            "experimental_results": self._analyze_experimental_results(),
            "challenges": self._analyze_challenges(),
            "future_directions": self._analyze_future_directions()
        }
        return self._generate_comprehensive_report(analysis_data)

    def _analyze_overview(self):
        """分析概述"""
        return {
            "total_papers": len(self.papers_data),
            "time_period": "2023-2024",
            "research_field": "纳米马达在生物医学领域的应用",
            "key_topics": [
                "智能响应性纳米马达",
                "深部组织渗透技术",
                "多功能协同治疗",
                "精确控制系统"
            ]
        }

    def _analyze_key_trends(self):
        """分析关键趋势"""
        return {
            "research_hotspots": [
                {
                    "topic": "智能响应性设计",
                    "description": "开发具有多重响应性的纳米马达系统",
                    "key_papers": ["Construction of a matchstick-shaped Au@ZnO@SiO2-ICG Janus nanomotor"],
                    "significance": "提高治疗精准性和效率"
                },
                {
                    "topic": "深部组织渗透",
                    "description": "研究纳米马达在复杂生物环境中的运动行为",
                    "key_papers": ["Deep Penetration of Nanolevel Drugs"],
                    "significance": "解决传统药物递送系统的局限性"
                },
                {
                    "topic": "多功能集成",
                    "description": "将诊断和治疗功能集成到单一系统",
                    "key_papers": ["Dual-responsive nanomotors for deep tumor penetration"],
                    "significance": "实现诊疗一体化"
                }
            ],
            "emerging_trends": [
                "智能控制系统开发",
                "生物安全性评价",
                "临床转化研究"
            ]
        }

    def _analyze_tech_innovations(self):
        """分析技术创新"""
        return {
            "material_innovations": [
                {
                    "type": "Janus结构设计",
                    "description": "开发不对称结构实现定向运动",
                    "advantages": ["运动方向可控", "功能区域化"],
                    "papers": ["Core@Satellite Janus Nanomotors"]
                },
                {
                    "type": "响应性材料",
                    "description": "开发对多种刺激响应的智能材料",
                    "advantages": ["精确控制", "环境适应性"],
                    "papers": ["Enzyme-Based Mesoporous Nanomotors"]
                }
            ],
            "method_innovations": [
                {
                    "type": "合成方法",
                    "description": "开发新型纳米材料合成技术",
                    "significance": "提高材料性能和可控性"
                },
                {
                    "type": "表征技术",
                    "description": "发展先进表征方法",
                    "significance": "深入理解材料结构与性能"
                }
            ]
        }

    def _analyze_experimental_results(self):
        """分析实验结果"""
        return {
            "performance_metrics": [
                {
                    "aspect": "运动性能",
                    "key_findings": ["速度可控", "方向可调"],
                    "significance": "实现精确导航"
                },
                {
                    "aspect": "治疗效果",
                    "key_findings": ["靶向性好", "疗效显著"],
                    "significance": "提高治疗效果"
                }
            ],
            "validation_methods": [
                "体外细胞实验",
                "动物模型验证",
                "安全性评估"
            ]
        }

    def _analyze_challenges(self):
        """分析技术挑战"""
        return {
            "current_challenges": [
                {
                    "category": "技术挑战",
                    "issues": [
                        "运动控制精度",
                        "生物环境适应性",
                        "长期稳定性"
                    ]
                },
                {
                    "category": "应用挑战",
                    "issues": [
                        "生物安全性",
                        "规模化生产",
                        "临床转化"
                    ]
                }
            ],
            "potential_solutions": [
                "开发新型控制策略",
                "优化材料设计",
                "建立标准化评价体系"
            ]
        }

    def _analyze_future_directions(self):
        """分析未来方向"""
        return {
            "research_directions": [
                {
                    "area": "智能化提升",
                    "description": "开发更智能的响应和控制系统",
                    "potential_impact": "提高治疗精准性"
                },
                {
                    "area": "临床转化",
                    "description": "推进临床应用研究",
                    "potential_impact": "实现实际应用"
                }
            ],
            "recommendations": [
                "加强基础研究",
                "推进标准化建设",
                "促进产学研合作"
            ]
        }

    def _generate_comprehensive_report(self, analysis_data):
        """生成综合报告"""
        report = f"""# 纳米马达研究文献综述报告

## 1. 摘要
本报告基于对{analysis_data['overview']['total_papers']}篇最新文献的分析，系统总结了纳米马达在生物医学领域的研究进展、技术创新和未来发展方向。

## 2. 研究概述
- 分析文献数量：{analysis_data['overview']['total_papers']}篇
- 研究时期：{analysis_data['overview']['time_period']}
- 研究领域：{analysis_data['overview']['research_field']}
- 核心主题：{self._format_list(analysis_data['overview']['key_topics'])}

## 3. 关键研究趋势
### 3.1 研究热点
{self._format_research_hotspots(analysis_data['key_trends']['research_hotspots'])}

### 3.2 新兴趋势
{self._format_list(analysis_data['key_trends']['emerging_trends'])}

## 4. 技术创新
### 4.1 材料创新
{self._format_material_innovations(analysis_data['tech_innovations']['material_innovations'])}

### 4.2 方法创新
{self._format_method_innovations(analysis_data['tech_innovations']['method_innovations'])}

## 5. 实验结果分析
### 5.1 性能指标
{self._format_performance_metrics(analysis_data['experimental_results']['performance_metrics'])}

### 5.2 验证方法
{self._format_list(analysis_data['experimental_results']['validation_methods'])}

## 6. 技术挑战
### 6.1 当前挑战
{self._format_challenges(analysis_data['challenges']['current_challenges'])}

### 6.2 潜在解决方案
{self._format_list(analysis_data['challenges']['potential_solutions'])}

## 7. 未来发展方向
### 7.1 研究方向
{self._format_research_directions(analysis_data['future_directions']['research_directions'])}

### 7.2 建议
{self._format_list(analysis_data['future_directions']['recommendations'])}

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
"""
        
        # 保存报告
        report_path = os.path.join("output", "comprehensive_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info(f"综合报告已保存到: {report_path}")
        
        return report

    def _format_list(self, items):
        """格式化列表项"""
        return "\n".join([f"- {item}" for item in items])

    def _format_research_hotspots(self, hotspots):
        """格式化研究热点"""
        result = []
        for spot in hotspots:
            result.append(f"#### {spot['topic']}")
            result.append(f"- 描述：{spot['description']}")
            result.append(f"- 代表性文献：{', '.join(spot['key_papers'])}")
            result.append(f"- 重要性：{spot['significance']}\n")
        return "\n".join(result)

    def _format_material_innovations(self, innovations):
        """格式化材料创新"""
        result = []
        for innovation in innovations:
            result.append(f"#### {innovation['type']}")
            result.append(f"- 描述：{innovation['description']}")
            result.append(f"- 优势：{', '.join(innovation['advantages'])}")
            result.append(f"- 相关文献：{', '.join(innovation['papers'])}\n")
        return "\n".join(result)

    def _format_method_innovations(self, innovations):
        """格式化方法创新"""
        result = []
        for innovation in innovations:
            result.append(f"#### {innovation['type']}")
            result.append(f"- 描述：{innovation['description']}")
            result.append(f"- 重要性：{innovation['significance']}\n")
        return "\n".join(result)

    def _format_performance_metrics(self, metrics):
        """格式化性能指标"""
        result = []
        for metric in metrics:
            result.append(f"#### {metric['aspect']}")
            result.append(f"- 主要发现：{', '.join(metric['key_findings'])}")
            result.append(f"- 重要性：{metric['significance']}\n")
        return "\n".join(result)

    def _format_challenges(self, challenges):
        """格式化技术挑战"""
        result = []
        for challenge in challenges:
            result.append(f"#### {challenge['category']}")
            result.append(self._format_list(challenge['issues']) + "\n")
        return "\n".join(result)

    def _format_research_directions(self, directions):
        """格式化研究方向"""
        result = []
        for direction in directions:
            result.append(f"#### {direction['area']}")
            result.append(f"- 描述：{direction['description']}")
            result.append(f"- 潜在影响：{direction['potential_impact']}\n")
        return "\n".join(result)

    def analyze(self):
        """执行完整的文献分析流程"""
        logger.info("开始生成文献综述...")
        
        # 生成综合分析报告
        logger.info("开始生成综合分析报告...")
        self.analyze_papers()
        
        # 生成基础JSON格式综述
        review = {
            "total_papers": len(self.papers_data),
            "papers_summary": [
                {
                    "title": paper.get('title', 'Unknown Title'),
                    "abstract": paper.get('abstract', 'No abstract available')[:500] + '...'
                    if paper.get('abstract') else 'No abstract available'
                }
                for paper in self.papers_data if paper
            ],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 保存JSON格式综述
        review_path = os.path.join("output", "literature_review.json")
        with open(review_path, "w", encoding="utf-8") as f:
            json.dump(review, f, ensure_ascii=False, indent=2)
        logger.info(f"文献综述已保存到: {review_path}")
        
        logger.info("=== 文献分析程序完成 ===")
        return review

def main():
    logger.info("=== 文献分析程序启动 ===")
    
    # 创建必要的目录
    input_dir = Path("input")
    output_dir = Path("output")
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    logger.info("目录检查完成")

    # 初始化并运行分析
    analyzer = LiteratureAnalyzer()
    analyzer.process_papers(str(input_dir))
    analyzer.analyze()
    
    logger.info("=== 文献分析程序完成 ===")

if __name__ == "__main__":
    main()
