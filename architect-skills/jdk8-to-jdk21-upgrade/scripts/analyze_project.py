#!/usr/bin/env python3
"""
JDK 8 to JDK 21 项目分析脚本
分析项目结构、依赖版本、代码使用情况，生成升级评估报告
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import xml.etree.ElementTree as ET

class ProjectAnalyzer:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.report = {
            'project_name': self.project_path.name,
            'analysis_time': datetime.now().isoformat(),
            'structure': {},
            'versions': {},
            'javax_usage': defaultdict(int),
            'deprecated_apis': [],
            'risks': [],
            'workload_estimate': {}
        }
    
    def analyze(self):
        """执行完整分析"""
        print(f"正在分析项目: {self.project_path}")
        print("=" * 60)
        
        self.analyze_structure()
        self.analyze_pom()
        self.analyze_java_files()
        self.assess_risks()
        self.estimate_workload()
        
        return self.report
    
    def analyze_structure(self):
        """分析项目结构"""
        print("\n[1/5] 分析项目结构...")
        
        pom_files = list(self.project_path.rglob('pom.xml'))
        java_files = list(self.project_path.rglob('*.java'))
        
        # 判断项目类型
        is_multi_module = len(pom_files) > 1
        has_spring_boot = any('spring-boot' in pom.read_text() for pom in pom_files)
        
        self.report['structure'] = {
            'type': 'multi-module' if is_multi_module else 'single-module',
            'is_spring_boot': has_spring_boot,
            'pom_count': len(pom_files),
            'java_files_count': len(java_files),
            'modules': [str(pom.parent.relative_to(self.project_path)) for pom in pom_files] if is_multi_module else []
        }
        
        print(f"  ✓ 项目类型: {'多模块' if is_multi_module else '单模块'}")
        print(f"  ✓ Spring Boot: {'是' if has_spring_boot else '否'}")
        print(f"  ✓ Java文件数: {len(java_files)}")
    
    def analyze_pom(self):
        """分析pom.xml配置"""
        print("\n[2/5] 分析Maven配置...")
        
        pom_path = self.project_path / 'pom.xml'
        if not pom_path.exists():
            print("  ⚠ 根目录未找到pom.xml")
            return
        
        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
            
            # 提取版本信息
            versions = {}
            
            # Java版本
            java_version = root.find('.//m:properties/m:java.version', ns)
            if java_version is not None:
                versions['java'] = java_version.text
            
            # Spring Boot版本
            parent = root.find('.//m:parent', ns)
            if parent is not None:
                artifact_id = parent.find('m:artifactId', ns)
                version = parent.find('m:version', ns)
                if artifact_id is not None and 'spring-boot' in artifact_id.text:
                    versions['spring_boot'] = version.text if version is not None else 'unknown'
            
            # Spring Cloud版本
            spring_cloud_version = root.find('.//m:properties/m:spring-cloud.version', ns)
            if spring_cloud_version is not None:
                versions['spring_cloud'] = spring_cloud_version.text
            
            self.report['versions'] = versions
            
            print(f"  ✓ JDK版本: {versions.get('java', '未指定')}")
            print(f"  ✓ Spring Boot: {versions.get('spring_boot', '未使用')}")
            print(f"  ✓ Spring Cloud: {versions.get('spring_cloud', '未使用')}")
            
        except Exception as e:
            print(f"  ✗ 解析pom.xml失败: {e}")
    
    def analyze_java_files(self):
        """分析Java源代码"""
        print("\n[3/5] 分析Java源代码...")
        
        java_files = list(self.project_path.rglob('*.java'))
        
        # javax命名空间使用统计
        javax_patterns = {
            'javax.servlet': r'import\s+javax\.servlet',
            'javax.persistence': r'import\s+javax\.persistence',
            'javax.validation': r'import\s+javax\.validation',
            'javax.annotation': r'import\s+javax\.annotation',
            'javax.transaction': r'import\s+javax\.transaction',
            'javax.ws.rs': r'import\s+javax\.ws\.rs',
        }
        
        # 过时API使用检测
        deprecated_patterns = {
            'sun.misc.Unsafe': r'import\s+sun\.misc\.Unsafe',
            'com.sun.*': r'import\s+com\.sun\.',
        }
        
        javax_files = defaultdict(set)
        deprecated_files = defaultdict(set)
        
        for java_file in java_files:
            try:
                content = java_file.read_text(encoding='utf-8')
                
                # 检测javax使用
                for pkg, pattern in javax_patterns.items():
                    if re.search(pattern, content):
                        self.report['javax_usage'][pkg] += 1
                        javax_files[pkg].add(str(java_file.relative_to(self.project_path)))
                
                # 检测过时API
                for api, pattern in deprecated_patterns.items():
                    matches = re.findall(pattern, content)
                    if matches:
                        deprecated_files[api].add(str(java_file.relative_to(self.project_path)))
                        
            except Exception as e:
                print(f"  ⚠ 读取文件失败: {java_file} - {e}")
        
        # 输出统计
        print(f"\n  javax命名空间使用统计:")
        for pkg, count in self.report['javax_usage'].items():
            print(f"    - {pkg}: {count}个文件")
        
        if deprecated_files:
            print(f"\n  ⚠ 发现过时API使用:")
            for api, files in deprecated_files.items():
                print(f"    - {api}: {len(files)}个文件")
                self.report['deprecated_apis'].append({
                    'api': api,
                    'files': list(files)
                })
    
    def assess_risks(self):
        """评估升级风险"""
        print("\n[4/5] 评估升级风险...")
        
        risks = []
        
        # 风险1: JDK版本跨度大
        current_jdk = self.report['versions'].get('java', '8')
        if current_jdk in ['1.6', '1.7', '6', '7']:
            risks.append({
                'level': 'HIGH',
                'item': 'JDK版本过低',
                'description': f'当前JDK {current_jdk}跨度过大，建议先升级到JDK 11',
                'impact': '可能存在大量不兼容问题'
            })
        
        # 风险2: Spring Boot版本
        spring_boot_version = self.report['versions'].get('spring_boot', '')
        if spring_boot_version and spring_boot_version.startswith('1.'):
            risks.append({
                'level': 'HIGH',
                'item': 'Spring Boot 1.x',
                'description': 'Spring Boot 1.x需要先升级到2.x',
                'impact': '无法直接升级到3.x'
            })
        
        # 风险3: javax使用量
        total_javax = sum(self.report['javax_usage'].values())
        if total_javax > 100:
            risks.append({
                'level': 'MEDIUM',
                'item': 'javax使用量大',
                'description': f'发现{total_javax}处javax命名空间使用',
                'impact': '需要大量代码迁移工作'
            })
        elif total_javax > 0:
            risks.append({
                'level': 'LOW',
                'item': 'javax使用',
                'description': f'发现{total_javax}处javax命名空间使用',
                'impact': '需要少量代码迁移工作'
            })
        
        # 风险4: 过时API
        if self.report['deprecated_apis']:
            risks.append({
                'level': 'HIGH',
                'item': '使用过时API',
                'description': f"发现{len(self.report['deprecated_apis'])}种过时API使用",
                'impact': '需要手动修复，可能无自动替代方案'
            })
        
        # 风险5: 多模块项目
        if self.report['structure']['type'] == 'multi-module':
            module_count = self.report['structure']['pom_count']
            risks.append({
                'level': 'MEDIUM',
                'item': '多模块项目',
                'description': f'包含{module_count}个模块',
                'impact': '需要协调各模块间的依赖版本'
            })
        
        self.report['risks'] = risks
        
        # 输出风险评估
        for risk in risks:
            level_symbol = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
            print(f"  {level_symbol.get(risk['level'], '⚪')} [{risk['level']}] {risk['item']}")
            print(f"     {risk['description']}")
    
    def estimate_workload(self):
        """估算工作量"""
        print("\n[5/5] 估算工作量...")
        
        # 基础工作量（小时）
        base_hours = 2
        
        # 根据项目规模调整
        java_count = self.report['structure']['java_files_count']
        if java_count > 500:
            base_hours += 8
        elif java_count > 200:
            base_hours += 4
        elif java_count > 50:
            base_hours += 2
        
        # 根据javax使用量调整
        javax_count = sum(self.report['javax_usage'].values())
        if javax_count > 0:
            base_hours += javax_count * 0.05  # 每个文件约3分钟
        
        # 根据风险调整
        high_risks = sum(1 for r in self.report['risks'] if r['level'] == 'HIGH')
        base_hours += high_risks * 2
        
        # 多模块项目调整
        if self.report['structure']['type'] == 'multi-module':
            module_count = self.report['structure']['pom_count']
            base_hours += module_count * 0.5
        
        self.report['workload_estimate'] = {
            'estimated_hours': round(base_hours, 1),
            'estimated_days': round(base_hours / 8, 1),
            'automation_coverage': '85%',
            'manual_work_hours': round(base_hours * 0.15, 1)
        }
        
        print(f"  ✓ 预估总工作量: {self.report['workload_estimate']['estimated_hours']}小时")
        print(f"  ✓ 预估工作天数: {self.report['workload_estimate']['estimated_days']}天")
        print(f"  ✓ 自动化覆盖: {self.report['workload_estimate']['automation_coverage']}")
        print(f"  ✓ 需人工处理: {self.report['workload_estimate']['manual_work_hours']}小时")
    
    def generate_report(self, output_path=None):
        """生成分析报告"""
        if output_path is None:
            output_path = self.project_path / 'upgrade_analysis_report.md'
        
        report_content = f"""# JDK升级分析报告 - {self.report['project_name']}

**分析时间**: {self.report['analysis_time']}

## 一、项目概况

- **项目类型**: {self.report['structure']['type']}
- **Spring Boot**: {'是' if self.report['structure']['is_spring_boot'] else '否'}
- **模块数量**: {self.report['structure']['pom_count']}
- **Java文件数**: {self.report['structure']['java_files_count']}

## 二、当前版本信息

- **JDK版本**: {self.report['versions'].get('java', '未指定')}
- **Spring Boot**: {self.report['versions'].get('spring_boot', '未使用')}
- **Spring Cloud**: {self.report['versions'].get('spring_cloud', '未使用')}

## 三、代码迁移需求

### javax命名空间使用统计

"""
        
        if self.report['javax_usage']:
            for pkg, count in self.report['javax_usage'].items():
                report_content += f"- `{pkg}`: {count}个文件\n"
        else:
            report_content += "✅ 未发现javax命名空间使用\n"
        
        report_content += "\n### 过时API使用\n\n"
        
        if self.report['deprecated_apis']:
            for api_info in self.report['deprecated_apis']:
                report_content += f"⚠️ **{api_info['api']}**: {len(api_info['files'])}个文件\n"
        else:
            report_content += "✅ 未发现过时API使用\n"
        
        report_content += "\n## 四、风险评估\n\n"
        
        for risk in self.report['risks']:
            level_symbol = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
            report_content += f"{level_symbol.get(risk['level'], '⚪')} **[{risk['level']}] {risk['item']}**\n"
            report_content += f"   - 描述: {risk['description']}\n"
            report_content += f"   - 影响: {risk['impact']}\n\n"
        
        report_content += f"""## 五、工作量估算

- **预估总工作量**: {self.report['workload_estimate']['estimated_hours']}小时
- **预估工作天数**: {self.report['workload_estimate']['estimated_days']}天
- **自动化覆盖率**: {self.report['workload_estimate']['automation_coverage']}
- **人工处理工作量**: {self.report['workload_estimate']['manual_work_hours']}小时

## 六、升级建议

### 推荐升级路径

1. **准备阶段** (0.5小时)
   - 创建备份分支
   - 准备测试环境
   - 通知相关团队

2. **配置升级阶段** (1-2小时)
   - 升级pom.xml配置
   - 更新依赖版本
   - 配置compiler plugin

3. **代码迁移阶段** ({round(sum(self.report['javax_usage'].values()) * 0.05, 1)}小时)
   - 批量转换javax到jakarta
   - 修复编译错误

4. **验证测试阶段** (2-4小时)
   - 运行单元测试
   - 执行集成测试
   - 性能基准测试

5. **问题修复阶段** ({self.report['workload_estimate']['manual_work_hours']}小时)
   - 处理特殊兼容性问题
   - 修复过时API调用

### 关键注意事项

- ⚠️ 升级前务必创建备份
- ⚠️ 建议在测试环境先验证
- ⚠️ 多模块项目建议分批升级
- ⚠️ 重点关注过时API的替代方案

## 七、下一步操作

执行升级命令：

```bash
# 1. 升级Maven配置
python scripts/upgrade_pom.py {self.project_path}/pom.xml --use-parent --backup

# 2. 迁移源代码
python scripts/migrate_imports.py {self.project_path}/src

# 3. 编译验证
bash scripts/validate_upgrade.sh {self.project_path}
```

---

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        output_path.write_text(report_content, encoding='utf-8')
        print(f"\n✅ 分析报告已生成: {output_path}")
        
        return output_path

def main():
    if len(sys.argv) < 2:
        print("用法: python analyze_project.py <project_path>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    
    if not os.path.exists(project_path):
        print(f"错误: 项目路径不存在: {project_path}")
        sys.exit(1)
    
    analyzer = ProjectAnalyzer(project_path)
    analyzer.analyze()
    
    # 生成报告
    report_path = analyzer.generate_report()
    
    print("\n" + "=" * 60)
    print("分析完成! 请查看详细报告了解升级建议。")
    print("=" * 60)
    
    # 输出JSON格式（供其他脚本使用）
    json_path = Path(project_path) / 'upgrade_analysis.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analyzer.report, f, indent=2, ensure_ascii=False)
    print(f"\nJSON报告: {json_path}")

if __name__ == '__main__':
    main()
