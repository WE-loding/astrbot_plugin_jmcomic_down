from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

import os,re
import sys
import shutil

import jmcomic  
from PIL import Image
import astrbot.api.message_components as Comp


#PDF导出路径
PDF_out = 'F:\jmcomic_files'




@register("jmcomic_down", "WE-loding", "下载禁漫本子", "1.0.1")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    @filter.command("jm")
    async def get_file(self,event):
        chain = [
            Comp.At(qq=event.get_sender_id()),  # At 消息发送者
            Comp.Plain(" 别急,我先找找,你急我也急（大约还需要等待30s）"),
        ]
        
        yield event.chain_result(chain)
        
        
        coimc_id = event.message_str        # 获取需要的漫画ID      
        img_folder = 'F:/jmcomic_files/{coimc_id}' # 下载输出路径
        
        message = event.message_str
        s=''.join(re.findall(r'\d+', message))
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        target_file = os.path.join(current_dir, 'option.yml')
        option = jmcomic.JmOption.from_file(target_file)
        jmcomic.download_album(s,option) #按照option规定的方式下载指定ID的漫画
    
        # 下载完成的使用所有图片，并按文件名升序排序
        img_files = [f for f in os.listdir(img_folder) if f.lower().endswith(('.jpg'))]
        img_files.sort()
        
        img_list = []
        
        # 依次打开所有图片，转换为RGB模式，加入列表
        for file in img_files:
            img_path = os.path.join(img_folder, file)
            img = Image.open(img_path).convert('RGB')
            img_list.append(img)
        
        # 设置导出为固定路径    
        pdf_path = os.path.join(PDF_out, f"{coimc_id}.pdf")
        
        # 设置第一页为封面，其余图片作为内容
        first_img = img_list[0]
        rest_imgs = []
        for img in img_list[1:]:
            rest_imgs.append(img)
        
        # 保存为PDF文件
        first_img.save(pdf_path, save_all=True, append_images=rest_imgs)

        # 删除图片文件夹
        shutil.rmtree(img_folder)

        file = [Comp.File(file=f"file://F:/JM_lib/download/{coimc_id}.pdf",name=f"{coimc_id}.pdf")]  # 从本地文件目录发送pdf
        
        chain = [
            Comp.At(qq=event.get_sender_id()),  # At 消息发送者
            Comp.Plain(" 虽然很艰难,但我还是导出来了"),
        ]
        shutil.rmtree('F:/jmcomic_files/{coimc_id}.pdf') # 清理垃圾
        
        yield event.chain_result(file)



