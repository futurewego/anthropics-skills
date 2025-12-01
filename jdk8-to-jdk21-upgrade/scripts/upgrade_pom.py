#!/usr/bin/env python3
"""
POM.xml自动升级脚本
将Maven配置升级到JDK 21兼容版本
"""

import os
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

class PomUpgrader:
    def __init__(self, pom_path, use_parent=False, backup=True):
        self.pom_path = Path(pom_path)
        self.use_parent = use_parent
        self.backup = backup
        self.ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        
        # 版本配置
        self.versions = {
            'spring_boot': '3.2.4',
            'spring_cloud': '2023.0.1',
            'lombok': '1.18.36',
            'mapstruct': '1.5.5.Final',
            'guava': '33.2.1-jre',
            'hutool': '5.8.25',
            'mybatis_plus': '3.5.5',
            'mysql_connector': '8.3.0',
            'redisson': '3.27.2',
            'fastjson2': '2.0.47',
        }
    
    def upgrade(self):
        """执行升级"""
        print(f"正在升级: {self.pom_path}")
        print("=" * 60)
        
        # 备份原文件
        if self.backup:
            self.create_backup()
        
        # 解析POM
        tree = ET.parse(self.pom_path)
        root = tree.getroot()
        
        # 注册命名空间
        ET.register_namespace('', 'http://maven.apache.org/POM/4.0.0')
        ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        
        # 执行升级操作
        if self.use_parent:
            self.upgrade_to_ym_parent(root)
        else:
            self.upgrade_with_bom(root)
        
        self.upgrade_properties(root)
        self.upgrade_dependencies(root)
        self.add_compiler_plugin(root)
        
        # 保存
        self.pretty_print(tree, root)
        tree.write(self.pom_path, encoding='UTF-8', xml_declaration=True)
        
        print("\n✅ POM升级完成!")
        print(f"   文件: {self.pom_path}")
        if self.backup:
            print(f"   备份: {self.pom_path}.backup")
    
    def create_backup(self):
        """创建备份文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{self.pom_path}.backup-{timestamp}"
        shutil.copy2(self.pom_path, backup_path)
        print(f"✓ 已创建备份: {backup_path}")
    
    def upgrade_to_ym_parent(self, root):
        """升级为继承ym-build-parent"""
        print("\n[1/5] 升级parent配置...")
        
        # 查找或创建parent元素
        parent = root.find('m:parent', self.ns)
        if parent is None:
            parent = ET.SubElement(root, '{http://maven.apache.org/POM/4.0.0}parent')
            # 插入到第一个位置
            root.insert(0, parent)
        else:
            # 清空现有parent内容
            parent.clear()
        
        # 设置新的parent
        group_id = ET.SubElement(parent, '{http://maven.apache.org/POM/4.0.0}groupId')
        group_id.text = 'com.ym'
        
        artifact_id = ET.SubElement(parent, '{http://maven.apache.org/POM/4.0.0}artifactId')
        artifact_id.text = 'ym-build-parent'
        
        version = ET.SubElement(parent, '{http://maven.apache.org/POM/4.0.0}version')
        version.text = '1.0.0-SNAPSHOT'
        
        print("  ✓ 已设置parent为ym-build-parent")
    
    def upgrade_with_bom(self, root):
        """使用BOM方式升级"""
        print("\n[1/5] 添加BOM依赖管理...")
        
        # 查找或创建dependencyManagement
        dep_mgmt = root.find('m:dependencyManagement', self.ns)
        if dep_mgmt is None:
            dep_mgmt = ET.SubElement(root, '{http://maven.apache.org/POM/4.0.0}dependencyManagement')
        
        # 查找或创建dependencies
        dependencies = dep_mgmt.find('m:dependencies', self.ns)
        if dependencies is None:
            dependencies = ET.SubElement(dep_mgmt, '{http://maven.apache.org/POM/4.0.0}dependencies')
        
        # 添加BOM
        bom = ET.SubElement(dependencies, '{http://maven.apache.org/POM/4.0.0}dependency')
        
        group_id = ET.SubElement(bom, '{http://maven.apache.org/POM/4.0.0}groupId')
        group_id.text = 'com.ym'
        
        artifact_id = ET.SubElement(bom, '{http://maven.apache.org/POM/4.0.0}artifactId')
        artifact_id.text = 'ym-dependencies-bom'
        
        version = ET.SubElement(bom, '{http://maven.apache.org/POM/4.0.0}version')
        version.text = '1.0.0-SNAPSHOT'
        
        type_elem = ET.SubElement(bom, '{http://maven.apache.org/POM/4.0.0}type')
        type_elem.text = 'pom'
        
        scope = ET.SubElement(bom, '{http://maven.apache.org/POM/4.0.0}scope')
        scope.text = 'import'
        
        print("  ✓ 已添加ym-dependencies-bom")
    
    def upgrade_properties(self, root):
        """升级properties配置"""
        print("\n[2/5] 升级版本属性...")
        
        # 查找或创建properties
        properties = root.find('m:properties', self.ns)
        if properties is None:
            properties = ET.SubElement(root, '{http://maven.apache.org/POM/4.0.0}properties')
        
        # 更新JDK版本
        java_properties = {
            'java.version': '21',
            'maven.compiler.source': '21',
            'maven.compiler.target': '21',
            'maven.compiler.release': '21',
        }
        
        for key, value in java_properties.items():
            prop = properties.find(f'm:{key}', self.ns)
            if prop is None:
                prop = ET.SubElement(properties, f'{{http://maven.apache.org/POM/4.0.0}}{key}')
            prop.text = value
        
        print("  ✓ JDK版本已设置为21")
        
        # 更新Spring版本（如果存在）
        spring_boot_prop = properties.find('m:spring-boot.version', self.ns)
        if spring_boot_prop is not None:
            spring_boot_prop.text = self.versions['spring_boot']
            print(f"  ✓ Spring Boot版本: {self.versions['spring_boot']}")
        
        spring_cloud_prop = properties.find('m:spring-cloud.version', self.ns)
        if spring_cloud_prop is not None:
            spring_cloud_prop.text = self.versions['spring_cloud']
            print(f"  ✓ Spring Cloud版本: {self.versions['spring_cloud']}")
    
    def upgrade_dependencies(self, root):
        """升级依赖版本"""
        print("\n[3/5] 升级依赖版本...")
        
        # 依赖版本映射
        dependency_upgrades = {
            ('org.projectlombok', 'lombok'): self.versions['lombok'],
            ('org.mapstruct', 'mapstruct'): self.versions['mapstruct'],
            ('com.google.guava', 'guava'): self.versions['guava'],
            ('cn.hutool', 'hutool-all'): self.versions['hutool'],
            ('com.baomidou', 'mybatis-plus-boot-starter'): self.versions['mybatis_plus'],
            ('com.mysql', 'mysql-connector-j'): self.versions['mysql_connector'],
            ('org.redisson', 'redisson-spring-boot-starter'): self.versions['redisson'],
            ('com.alibaba.fastjson2', 'fastjson2'): self.versions['fastjson2'],
        }
        
        # 查找所有dependencies节点
        for dependencies in root.findall('.//m:dependencies', self.ns):
            for dependency in dependencies.findall('m:dependency', self.ns):
                group_id = dependency.find('m:groupId', self.ns)
                artifact_id = dependency.find('m:artifactId', self.ns)
                
                if group_id is not None and artifact_id is not None:
                    key = (group_id.text, artifact_id.text)
                    if key in dependency_upgrades:
                        version = dependency.find('m:version', self.ns)
                        if version is None:
                            version = ET.SubElement(dependency, '{http://maven.apache.org/POM/4.0.0}version')
                        version.text = dependency_upgrades[key]
                        print(f"  ✓ 升级: {artifact_id.text} -> {dependency_upgrades[key]}")
    
    def add_compiler_plugin(self, root):
        """添加compiler plugin配置（仅BOM模式需要）"""
        if self.use_parent:
            print("\n[4/5] 跳过compiler plugin配置（由parent提供）")
            return
        
        print("\n[4/5] 配置compiler plugin...")
        
        # 查找或创建build节点
        build = root.find('m:build', self.ns)
        if build is None:
            build = ET.SubElement(root, '{http://maven.apache.org/POM/4.0.0}build')
        
        # 查找或创建plugins节点
        plugins = build.find('m:plugins', self.ns)
        if plugins is None:
            plugins = ET.SubElement(build, '{http://maven.apache.org/POM/4.0.0}plugins')
        
        # 检查是否已有compiler plugin
        existing_plugin = None
        for plugin in plugins.findall('m:plugin', self.ns):
            artifact_id = plugin.find('m:artifactId', self.ns)
            if artifact_id is not None and artifact_id.text == 'maven-compiler-plugin':
                existing_plugin = plugin
                break
        
        if existing_plugin is not None:
            plugins.remove(existing_plugin)
        
        # 创建新的compiler plugin
        plugin = ET.SubElement(plugins, '{http://maven.apache.org/POM/4.0.0}plugin')
        
        group_id = ET.SubElement(plugin, '{http://maven.apache.org/POM/4.0.0}groupId')
        group_id.text = 'org.apache.maven.plugins'
        
        artifact_id = ET.SubElement(plugin, '{http://maven.apache.org/POM/4.0.0}artifactId')
        artifact_id.text = 'maven-compiler-plugin'
        
        version = ET.SubElement(plugin, '{http://maven.apache.org/POM/4.0.0}version')
        version.text = '3.11.0'
        
        # configuration节点
        configuration = ET.SubElement(plugin, '{http://maven.apache.org/POM/4.0.0}configuration')
        
        source = ET.SubElement(configuration, '{http://maven.apache.org/POM/4.0.0}source')
        source.text = '21'
        
        target = ET.SubElement(configuration, '{http://maven.apache.org/POM/4.0.0}target')
        target.text = '21'
        
        release = ET.SubElement(configuration, '{http://maven.apache.org/POM/4.0.0}release')
        release.text = '21'
        
        fork = ET.SubElement(configuration, '{http://maven.apache.org/POM/4.0.0}fork')
        fork.text = 'true'
        
        # annotationProcessorPaths
        processor_paths = ET.SubElement(configuration, '{http://maven.apache.org/POM/4.0.0}annotationProcessorPaths')
        
        # Lombok
        lombok_path = ET.SubElement(processor_paths, '{http://maven.apache.org/POM/4.0.0}path')
        lombok_group = ET.SubElement(lombok_path, '{http://maven.apache.org/POM/4.0.0}groupId')
        lombok_group.text = 'org.projectlombok'
        lombok_artifact = ET.SubElement(lombok_path, '{http://maven.apache.org/POM/4.0.0}artifactId')
        lombok_artifact.text = 'lombok'
        lombok_version = ET.SubElement(lombok_path, '{http://maven.apache.org/POM/4.0.0}version')
        lombok_version.text = self.versions['lombok']
        
        # MapStruct
        mapstruct_path = ET.SubElement(processor_paths, '{http://maven.apache.org/POM/4.0.0}path')
        mapstruct_group = ET.SubElement(mapstruct_path, '{http://maven.apache.org/POM/4.0.0}groupId')
        mapstruct_group.text = 'org.mapstruct'
        mapstruct_artifact = ET.SubElement(mapstruct_path, '{http://maven.apache.org/POM/4.0.0}artifactId')
        mapstruct_artifact.text = 'mapstruct-processor'
        mapstruct_version = ET.SubElement(mapstruct_path, '{http://maven.apache.org/POM/4.0.0}version')
        mapstruct_version.text = self.versions['mapstruct']
        
        # compilerArgs
        compiler_args = ET.SubElement(configuration, '{http://maven.apache.org/POM/4.0.0}compilerArgs')
        
        arg1 = ET.SubElement(compiler_args, '{http://maven.apache.org/POM/4.0.0}arg')
        arg1.text = '-Amapstruct.suppressGeneratorTimestamp=true'
        
        arg2 = ET.SubElement(compiler_args, '{http://maven.apache.org/POM/4.0.0}arg')
        arg2.text = '-Amapstruct.defaultComponentModel=spring'
        
        arg3 = ET.SubElement(compiler_args, '{http://maven.apache.org/POM/4.0.0}arg')
        arg3.text = '--add-opens'
        
        arg4 = ET.SubElement(compiler_args, '{http://maven.apache.org/POM/4.0.0}arg')
        arg4.text = 'jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED'
        
        print("  ✓ 已配置maven-compiler-plugin")
    
    def pretty_print(self, tree, root):
        """格式化XML输出"""
        self.indent(root)
    
    def indent(self, elem, level=0):
        """递归缩进XML元素"""
        i = "\n" + level * "    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self.indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

def main():
    if len(sys.argv) < 2:
        print("用法: python upgrade_pom.py <pom.xml路径> [--use-parent] [--no-backup]")
        print("\n选项:")
        print("  --use-parent  使用ym-build-parent继承方式（推荐）")
        print("  --no-backup   不创建备份文件")
        sys.exit(1)
    
    pom_path = sys.argv[1]
    use_parent = '--use-parent' in sys.argv
    backup = '--no-backup' not in sys.argv
    
    if not os.path.exists(pom_path):
        print(f"错误: 文件不存在: {pom_path}")
        sys.exit(1)
    
    upgrader = PomUpgrader(pom_path, use_parent=use_parent, backup=backup)
    
    try:
        upgrader.upgrade()
        print("\n" + "=" * 60)
        print("升级完成! 建议执行以下命令验证:")
        print("  mvn clean compile")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 升级失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
