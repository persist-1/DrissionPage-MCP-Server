#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文本匹配算法模块

提供多层次的文本匹配策略，解决元素选择器的精确性和灵活性问题。
支持完全匹配、前缀匹配、包含匹配和模糊匹配，并提供置信度评分。

作者: DrissionPage MCP 项目管理工程师
创建时间: 2025-09-01
"""

import re
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class MatchResult:
    """匹配结果数据类"""
    element: Any  # 匹配到的元素对象
    text: str  # 元素文本内容
    score: float  # 匹配置信度 (0.0-1.0)
    strategy: str  # 匹配策略名称
    reason: str  # 匹配原因说明


class TextMatcher:
    """智能文本匹配器
    
    实现多层次匹配策略：
    1. 完全匹配 (exact) - 置信度 1.0
    2. 前缀匹配 (prefix) - 置信度 0.9
    3. 包含匹配 (contains) - 置信度 0.8 - 长度惩罚
    4. 模糊匹配 (fuzzy) - 基于编辑距离的相似度
    """
    
    def __init__(self, fuzzy_threshold: float = 0.6, case_sensitive: bool = False):
        """
        初始化文本匹配器
        
        Args:
            fuzzy_threshold: 模糊匹配的最低相似度阈值
            case_sensitive: 是否区分大小写
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.case_sensitive = case_sensitive
    
    def match_elements(self, target_text: str, elements: List[Tuple[Any, str]]) -> List[MatchResult]:
        """
        对元素列表进行智能文本匹配
        
        Args:
            target_text: 目标文本
            elements: 元素列表，每个元素为 (element_object, element_text) 元组
            
        Returns:
            按置信度降序排列的匹配结果列表
        """
        if not target_text or not elements:
            return []
        
        # 预处理目标文本
        processed_target = self._preprocess_text(target_text)
        
        results = []
        
        for element, element_text in elements:
            if not element_text:
                continue
                
            processed_element_text = self._preprocess_text(element_text)
            
            # 尝试各种匹配策略
            match_result = self._try_match_strategies(
                processed_target, processed_element_text, element, element_text
            )
            
            if match_result:
                results.append(match_result)
        
        # 按置信度降序排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def get_best_match(self, target_text: str, elements: List[Tuple[Any, str]]) -> Optional[MatchResult]:
        """
        获取最佳匹配结果
        
        Args:
            target_text: 目标文本
            elements: 元素列表
            
        Returns:
            最佳匹配结果，如果没有匹配则返回None
        """
        results = self.match_elements(target_text, elements)
        return results[0] if results else None
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        if not self.case_sensitive:
            text = text.lower()
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def _try_match_strategies(self, target: str, element_text: str, element: Any, original_text: str) -> Optional[MatchResult]:
        """尝试各种匹配策略"""
        
        # 1. 完全匹配 - 最高优先级
        if target == element_text:
            return MatchResult(
                element=element,
                text=original_text,
                score=1.0,
                strategy="exact",
                reason=f"完全匹配: '{target}'"
            )
        
        # 2. 前缀匹配 - 适用于按钮文本等场景
        if element_text.startswith(target):
            return MatchResult(
                element=element,
                text=original_text,
                score=0.9,
                strategy="prefix",
                reason=f"前缀匹配: '{target}' 是 '{element_text}' 的前缀"
            )
        
        # 3. 包含匹配 - 当前逻辑，但添加长度惩罚
        if target in element_text:
            # 计算长度惩罚：目标文本越短，元素文本越长，惩罚越大
            length_penalty = (len(target) / len(element_text)) * 0.3
            score = 0.8 - (1 - length_penalty)
            score = max(score, 0.5)  # 确保最低分不低于0.5
            
            return MatchResult(
                element=element,
                text=original_text,
                score=score,
                strategy="contains",
                reason=f"包含匹配: '{element_text}' 包含 '{target}' (长度比: {len(target)}/{len(element_text)})"
            )
        
        # 4. 模糊匹配 - 基于编辑距离的相似度
        similarity = self._calculate_similarity(target, element_text)
        if similarity >= self.fuzzy_threshold:
            return MatchResult(
                element=element,
                text=original_text,
                score=similarity,
                strategy="fuzzy",
                reason=f"模糊匹配: 相似度 {similarity:.2f} (阈值: {self.fuzzy_threshold})"
            )
        
        return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        if not text1 or not text2:
            return 0.0
        
        # 使用SequenceMatcher计算相似度
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio()
    
    def get_match_statistics(self, results: List[MatchResult]) -> Dict[str, int]:
        """获取匹配策略统计信息"""
        stats = {"exact": 0, "prefix": 0, "contains": 0, "fuzzy": 0}
        for result in results:
            if result.strategy in stats:
                stats[result.strategy] += 1
        return stats


# 默认匹配器实例
default_matcher = TextMatcher()


def smart_text_match(target_text: str, elements: List[Tuple[Any, str]], 
                    fuzzy_threshold: float = 0.6, case_sensitive: bool = False) -> List[MatchResult]:
    """便捷的智能文本匹配函数
    
    Args:
        target_text: 目标文本
        elements: 元素列表
        fuzzy_threshold: 模糊匹配阈值
        case_sensitive: 是否区分大小写
        
    Returns:
        匹配结果列表
    """
    matcher = TextMatcher(fuzzy_threshold=fuzzy_threshold, case_sensitive=case_sensitive)
    return matcher.match_elements(target_text, elements)


def get_best_text_match(target_text: str, elements: List[Tuple[Any, str]], 
                       fuzzy_threshold: float = 0.6, case_sensitive: bool = False) -> Optional[MatchResult]:
    """便捷的最佳匹配获取函数
    
    Args:
        target_text: 目标文本
        elements: 元素列表
        fuzzy_threshold: 模糊匹配阈值
        case_sensitive: 是否区分大小写
        
    Returns:
        最佳匹配结果
    """
    matcher = TextMatcher(fuzzy_threshold=fuzzy_threshold, case_sensitive=case_sensitive)
    return matcher.get_best_match(target_text, elements)