# 🎨 文生图Prompt指南
更新时间：2025-05-22 16:12:38

## 📋 适用范围
- 通义万相-文生图V2版
- 通义万相-文生图V1版

## 🔧 提示词参数
文生图模型有两个参数跟提示词有关：

- **prompt**：正向提示词，支持中英文。需要用一段文字描述所需生成的图片。本文的提示词技巧指的是 prompt 的撰写技巧。
- **negative_prompt**：反向提示词，描述不希望在图像中看到的内容。

**文生图V2支持**：
- **prompt_extend**：是否开启prompt智能改写。默认为true，即开启大模型智能改写。推荐使用默认配置。

```json
{
    "input": {
        "prompt": "一间有着精致窗户的花店，漂亮的木质门，摆放着花朵",
        "negative_prompt": "人物"
    },
    "parameters": {
        "prompt_extend": true
    }
}
```

## 🎯 提示词公式

### 基础公式
**面向用户**：适用于初次尝试AI创作的新用户，及将AI作为灵感启发的用户，简单自由的提示词可生成更具有想象力的图像。

```
提示词 = 主体 + 场景 + 风格
```

- **主体**：主体是图片内容的主要表现对象，可以是人、动物、植物、物品或非物理真实存在的想象之物。
- **场景**：场景是主体所处的环境，包括室内或室外、季节、天气、光线等可以是物理存在的真实空间或想象出来的虚构场景。
- **风格**：选择或定义图像的艺术风格，如写实，抽象等，有助于模型生成具有特定视觉效果的图像。

#### 基础公式示例
**提示词**：
```
25岁中国女孩，圆脸，看着镜头，优雅的民族服装，商业摄影，室外，电影级光照，半身特写，精致的淡妆，锐利的边缘。
```

### 进阶公式
**面向用户**：适用于有一定AI生图使用经验的用户，在基础公式之上添加更丰富细致的描述可有效提升画面质感、细节丰富度与表现力。

```
提示词 = 主体（主体描述）+ 场景（场景描述）+ 风格（定义风格）+ 镜头语言 + 氛围词 + 细节修饰
```

- **主体描述**：确定主体清晰地描述图像中的主体，包括其特征、动作等。例如，"一个可爱的10岁中国小女孩，穿着红色衣服"。
- **场景描述**：场景描述是对主体所处环境特征细节的描述，可通过形容词或短句列举。
- **定义风格**：定义风格是明确地描述图像所应具有的特定艺术风格、表现手法或视觉特征。例如，"水彩风格"、"漫画风格"。
- **镜头语言**：镜头语言包含景别、视角等。
- **氛围词**：氛围词是对预期画面氛围的描述，例如"梦幻"、"孤独"、"宏伟"。
- **细节修饰**：细节修饰是对画面进一步的精细化和优化，以增强图像的细节表现力、丰富度和美感。例如"光源的位置"、"道具搭配"、"环境细节"、"高分辨率"等。

#### 进阶公式示例
**提示词**：
```
由羊毛毡制成的大熊猫，头戴大檐帽，穿着蓝色警服马甲，扎着腰带，携带警械装备，戴着蓝色手套，穿着皮鞋，大步奔跑姿态，毛毡效果，周围是动物王国城市街道商户，高级滤镜，路灯，动物王国，奇妙童趣，憨态可掬，夜晚，明亮，自然，可爱，4K，毛毡材质，摄影镜头，居中构图，毛毡风格，皮克斯风格，逆光。
```

## 📚 提示词词典
通过撰写不同维度的提示词，决定了生成图像的内容、风格、细节等多个方面的表现力。

### 1. 景别
景别是指由于相机与被拍摄体的距离不同，而造成被摄体在图像画面中所呈现出的范围大小的区别。

| 景别类型 | 提示词示例 |
|---------|-----------|
| 特写 | 特写镜头、高清相机、情绪大片、日落、特写人像 |
| 近景 | 近景镜头、18岁的中国女孩、古代服饰、圆脸、看着镜头、民族优雅的服装、商业摄影、室外、电影级光照、半身特写、精致的淡妆、锐利的边缘 |
| 中景 | 电影时尚魅力摄影、年轻亚洲女子、中国苗族女孩、圆脸、看着镜头、民族深色优雅的服装、中广角镜头、阳光明媚、乌托邦式、由高清相机拍摄 |
| 远景 | 展示了远景镜头、在壮丽的雪山背景下、两个小小的人影站在远处山顶、背对着镜头、静静地观赏着日落的美景、夕阳的余晖洒在雪山上、呈现出一片金黄色的光辉 |

### 2. 视角
镜头视角，即相机拍摄画面时所选取的视角。

| 视角类型 | 提示词示例 |
|---------|-----------|
| 平视 | 平视视角、图像展示了从平视视角捕捉到的草地景象、一群羊悠闲地在绿茵茵的草地上低头觅食 |
| 俯视 | 俯视视角、我从空中俯瞰冰湖、中心有一艘小船、周围环绕着漩涡图案和充满活力的蓝色海水 |
| 仰视 | 仰视视角、展示了热带地区的壮观景象、高大的椰子树如同参天巨人般耸立、枝叶茂盛、直指蓝天 |
| 航拍 | 航拍视角、展示了大雪、村庄、道路、灯火、树木、航拍视角、逼真效果 |

### 3. 镜头拍摄类型
镜头拍摄类型是指相机镜头根据不同的焦距、功能、应用场景等所划分的不同种类。

| 镜头类型 | 提示词示例 |
|---------|-----------|
| 微距 | 微距镜头、cherries、carbonated water、macro、professional color grading、clean sharp focus、commercial high quality、magazine winning photography、hyper realistic、uhd、8K |
| 超广角 | 超广角镜头、碧海蓝天下的海岛、阳光透过树叶缝隙、洒下斑驳光影 |
| 长焦 | 长焦镜头、展示了长焦镜头下、一只猎豹在郁郁葱葱的森林中站立、面对镜头、背景被巧妙地虚化 |
| 鱼眼 | 鱼眼镜头、展示了在鱼眼镜头的特殊视角下、一位女性站立着并直视镜头的场景 |

### 4. 风格
定义风格是明确地描述图像所应具有的特定艺术风格、表现手法或视觉特征。

| 风格类型 | 提示词示例 |
|---------|-----------|
| 3D卡通 | 网球女运动员、短发、白色网球服、黑色短裤、侧身回球、3D卡通风格 |
| 废土风 | 火星上的城市、废土风格 |
| 点彩画 | 一座白色的可爱的小房子、茅草房、一片被雪覆盖的草原、大胆使用点彩色画、莫奈感、清晰的笔触、边缘模糊 |
| 超现实 | 深灰色大海中一条粉红色的发光河流、具有极简、美丽和审美的氛围、具有超现实风格的电影灯光 |
| 水彩 | 浅水彩、咖啡馆外、明亮的白色背景、更少细节、梦幻、吉卜力工作室 |
| 粘土 | 粘土风格、蓝色毛衣的小男孩、棕色卷发、深蓝色贝雷帽、画板、户外、海边、半身照 |
| 写实 | 篮子、葡萄、野餐布、超写实静物摄影、微距镜头、丁达尔效应 |
| 陶瓷 | 展示了高细节的瓷器小狗、它静静地躺在桌上、脖子上系着一个精致的铃铛 |
| 3D | 中国龙、可爱的中国龙睡在白云上、迷人的花园、在晨雾中、特写、正面、3D立体、C4D渲染、32k超高清 |
| 水墨 | 兰花、水墨画、留白、意境、吴冠中风格、细腻的笔触、宣纸的纹理 |
| 折纸 | 折纸杰作、牛皮纸材质的熊猫、森林背景、中景、极简主义、背光、最佳品质 |
| 工笔 | 晨曦中、一枝寒梅傲立雪中、花瓣细腻如丝、露珠轻挂、展现工笔画之精致美 |
| 国风水墨 | 国风水墨风格、一个长长黑发的男人、金色的发簪、飞舞着金色的蝴蝶、白色的服装、高细节、高质量、深蓝色背景 |

### 5. 光线
不同的光线类型可以创造出各种不同的氛围和效果，满足不同的创作需求。

| 光线类型 | 提示词示例 |
|---------|-----------|
| 自然光 | 太阳光、月光、星光、早晨的阳光洒在一片茂密森林的地面上、银白色的光芒穿透树梢、形成斑驳陆离的光影 |
| 逆光 | 逆光、展示了在逆光环境下、模特轮廓线条更加分明、金色的光线以及丝绸环绕在模特周围、形成梦幻般的光环效果 |
| 霓虹灯 | 霓虹灯、雨后的城市街景、霓虹灯光在湿润的地面上反射出绚丽多彩的光芒、行人撑伞匆匆走过 |
| 氛围光 | 氛围光、夜晚河边的浪漫艺术景象、氛围灯温柔地照亮了水面、一群莲花灯缓缓飘向河心 |

## 📝 实用提示词模板

### 基础模板
```
[主体] + [场景] + [风格]
```

### 进阶模板
```
[主体描述] + [场景描述] + [定义风格] + [镜头语言] + [氛围词] + [细节修饰]
```

## 🎯 文字渲染能力展示

### 中文渲染案例
**案例1**：宫崎骏动漫风格场景
```
宫崎骏的动漫风格。平视角拍摄，阳光下的古街热闹非凡。一个穿着青衫、手里拿着写着"阿里云"卡片的逍遥派弟子站在中间。旁边两个小孩惊讶的看着他。左边有一家店铺挂着"云存储"的牌子，里面摆放着发光的服务器机箱，门口两个侍卫守护者。右边有两家店铺，其中一家挂着"云计算"的牌子，一个穿着旗袍的美丽女子正看着里面闪闪发光的电脑屏幕；另一家店铺挂着"云模型"的牌子，门口放着一个大酒缸，上面写着"千问"，一位老板娘正在往里面倒发光的代码溶液。
```

**案例2**：典雅对联
```
一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，对联上左书"义本生知人机同道善思新"，右书"通云赋智乾坤启数高志远"，横批"智启通义"，字体飘逸，中间挂在一着一副中国风的画作，内容是岳阳楼。
```

### 英文渲染案例
**案例1**：书店橱窗
```
Bookstore window display. A sign displays "New Arrivals This Week". Below, a shelf tag with the text "Best-Selling Novels Here". To the side, a colorful poster advertises "Author Meet And Greet on Saturday" with a central portrait of the author. There are four books on the bookshelf, namely "The light between worlds" "When stars are scattered" "The slient patient" "The night circus".
```

**案例2**：复杂信息图表
```
A slide featuring artistic, decorative shapes framing neatly arranged textual information styled as an elegant infographic. At the very center, the title "Habits for Emotional Wellbeing" appears clearly, surrounded by a symmetrical floral pattern. On the left upper section, "Practice Mindfulness" appears next to a minimalist lotus flower icon, with the short sentence, "Be present, observe without judging, accept without resisting". Next, moving downward, "Cultivate Gratitude" is written near an open hand illustration, along with the line, "Appreciate simple joys and acknowledge positivity daily". Further down, towards bottom-left, "Stay Connected" accompanied by a minimalistic chat bubble icon reads "Build and maintain meaningful relationships to sustain emotional energy". At bottom right corner, "Prioritize Sleep" is depicted next to a crescent moon illustration, accompanied by the text "Quality sleep benefits both body and mind". Moving upward along the right side, "Regular Physical Activity" is near a jogging runner icon, stating: "Exercise boosts mood and relieves anxiety". Finally, at the top right side, appears "Continuous Learning" paired with a book icon, stating "Engage in new skill and knowledge for growth".
```

**案例3**：小文字渲染
```
A man in a suit is standing in front of the window, looking at the bright moon outside the window. The man is holding a yellowed paper with handwritten words on it: "A lantern moon climbs through the silver night, Unfurling quiet dreams across the sky, Each star a whispered promise wrapped in light, That dawn will bloom, though darkness wanders by." There is a cute cat on the windowsill.
```

**案例4**：大段文字渲染
```
一个穿着"QWEN"标志的T恤的中国美女正拿着黑色的马克笔面向镜头微笑。她身后的玻璃板上手写体写着 "一、Qwen-Image的技术路线： 探索视觉生成基础模型的极限，开创理解与生成一体化的未来。二、Qwen-Image的模型特色：1、复杂文字渲染。支持中英渲染、自动布局； 2、精准图像编辑。支持文字编辑、物体增减、风格变换。三、Qwen-Image的未来愿景：赋能专业内容创作、助力生成式AI发展。"
```

**案例5**：企业级PPT
```
一张企业级高质量PPT页面图像，整体采用科技感十足的星空蓝为主色调，背景融合流动的发光科技线条与微光粒子特效，营造出专业、现代且富有信任感的品牌氛围；页面顶部左侧清晰展示橘红色Alibaba标志，色彩鲜明、辨识度高。主标题位于画面中央偏上位置，使用大号加粗白色或浅蓝色字体写着"通义千问视觉基础模型"，字体现代简洁，突出技术感；主标题下方紧接一行楷体中文文字："原生中文·复杂场景·自动布局"，字体柔和优雅，形成科技与人文的融合。下方居中排布展示了四张与图片，分别是：一幅写实与水墨风格结合的梅花特写，枝干苍劲、花瓣清雅，背景融入淡墨晕染与飘雪效果，体现坚韧不拔的精神气质；上方写着黑色的楷体"梅傲"。一株生长于山涧石缝中的兰花，叶片修长、花朵素净，搭配晨雾缭绕的自然环境，展现清逸脱俗的文人风骨；上方写着黑色的楷体"兰幽"。一组迎风而立的翠竹，竹叶随风摇曳，光影交错，背景为青灰色山岩与流水，呈现刚柔并济、虚怀若谷的文化意象；上方写着黑色的楷体"竹清"。一片盛开于秋日庭院的菊花丛，花色丰富、层次分明，配以落叶与古亭剪影，传递恬然自适的生活哲学；上方写着黑色的楷体"菊淡"。所有图片采用统一尺寸与边框样式，呈横向排列。页面底部中央用楷体小字写明"2025年8月，敬请期待"，排版工整、结构清晰，整体风格统一且细节丰富，极具视觉冲击力与品牌调性。
```

### 双语渲染案例
```
一个穿着"QWEN"标志的T恤的中国美女正拿着黑色的马克笔面向镜头微笑。她身后的玻璃板上手写体写着"Meet Qwen-Image – a powerful image foundation model capable of complex text rendering and precise image editing. 欢迎了解Qwen-Image, 一款强大的图像基础模型，擅长复杂文本渲染与精准图像编辑"
```

**案例6**：电影海报
```
A movie poster. The first row is the movie title, which reads "Imagination Unleashed". The second row is the movie subtitle, which reads "Enter a world beyond your imagination". The third row reads "Cast: Qwen-Image". The fourth row reads "Director: The Collective Imagination of Humanity". The central visual features a sleek, futuristic computer from which radiant colors, whimsical creatures, and dynamic, swirling patterns explosively emerge, filling the composition with energy, motion, and surreal creativity. The background transitions from dark, cosmic tones into a luminous, dreamlike expanse, evoking a digital fantasy realm. At the bottom edge, the text "Launching in the Cloud, August 2025" appears in bold, modern sans-serif font with a glowing, slightly transparent effect, evoking a high-tech, cinematic aesthetic. The overall style blends sci-fi surrealism with graphic design flair—sharp contrasts, vivid color grading, and layered visual depth—reminiscent of visionary concept art and digital matte painting, 32K resolution, ultra-detailed.
```

## 📋 快速使用模板

### 人像类
```
[年龄][国籍]人，[面部特征]，[服装描述]，[摄影风格]，[环境]，[光线]，[景别]，[细节修饰]
```

### 风景类
```
[时间][季节]，[地点/景物]，[艺术风格]，[光线条件]，[氛围词]，[细节修饰]
```

### 产品类
```
[产品名称]，[材质/颜色]，[展示角度]，[风格定义]，[光线设置]，[背景描述]
```

## 🔍 使用建议

1. **新手建议**：从基础公式开始，逐步添加更多描述元素
2. **进阶用户**：使用进阶公式，结合提示词词典中的具体描述
3. **文字渲染**：Qwen-Image模型在中文和英文文字渲染方面表现出色
4. **风格选择**：参考风格词典中的具体提示词，确保风格准确性
5. **细节控制**：使用镜头语言和光线描述来精确控制画面效果