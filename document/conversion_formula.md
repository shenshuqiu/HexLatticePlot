# 轴坐标
## 轴坐标参数
`x`：行数，正方向向右
`z`：列数，正方向向下

## 轴坐标示例：
```
    (0,-1)    (1,-1)  
(-1,0)    (0,0)    (1,0)
    (-1,1)    (0,1)
```

## 轴坐标转换

### 轴坐标转换为笛卡尔坐标

轴坐标 $(x',z')$ 转换为笛卡尔坐标 $(x, z)$

$$
\begin{equation}
\left[
\begin{matrix}
    1 & 1/2 \\
    0 & -\sqrt{3}/2
\end{matrix}
\right]
\left[
\begin{array}{c}
    x' \\
    z'
\end{array}
\right] =
\left[
\begin{array}{c}
    x \\
    z
\end{array}
\right]
\end{equation}
$$

### 笛卡尔坐标转换为轴坐标

笛卡尔坐标 $(x, z)$转换为轴坐标 $(x',z')$ 

$$
\begin{equation}
\left[
\begin{matrix}
    1 & 1/\sqrt{3} \\
    0 & -2/\sqrt{3}
\end{matrix}
\right]
\left[
\begin{array}{c}
    x \\
    z
\end{array}
\right] =
\left[
\begin{array}{c}
    x' \\
    z'
\end{array}
\right]
\end{equation}
$$

---
# 环坐标

## 环坐标参数
 `r`：到原点的距离
 `k`：顺时针序数

## 环坐标系示例：

```
    (1,4)   (1,5)
(1,3)   (0,0)   (1,0)
    (1,2)   (1,1)
```

## 环坐标转换

### 环坐标转换为轴坐标

#### 1. 环坐标转换为笛卡尔坐标
$(r, k) \rightarrow (r\cos(\frac{k\pi}{3r})$, $-r\sin(\frac{k\pi}{3r}))$

#### 2. 再由笛卡尔坐标转换为轴坐标
轴坐标 $(x,z)$，环坐标 $(r, k )$ 
$$
\begin{equation}
\left[
\begin{matrix}
    1 & 1/\sqrt{3} \\
    0 & -2/\sqrt{3}
\end{matrix}
\right]
\left[
\begin{array}{c}
    r\cos(k\pi/3r) \\
    -r\sin(k\pi/3r)
\end{array}
\right] =
\left[
\begin{array}{c}
    x \\
    z
\end{array}
\right]
\end{equation}
$$

即

$$
\begin{equation}
\left\{\begin{array}{rl}
    x= & r\cdot(\cos(\frac{k\pi}{3r})-\frac{1}{\sqrt{3}}\sin(\frac{k\pi}{3r})) \\
    z= & \frac{2}{\sqrt{3}} r\cdot\sin(\frac{k\pi}{3r})
\end{array}\right.
\end{equation}
$$

### 轴坐标转换为环坐标
轴坐标 $(x,z)$，环坐标 $(r, k )$

#### 1. 轴坐标转换为笛卡尔坐标

轴坐标 $(x,z)$ 转换为笛卡尔坐标 $(x', z')$

$$
\begin{equation}
\left[
\begin{matrix}
    1 & 1/2 \\
    0 & -\sqrt{3}/2
\end{matrix}
\right]
\left[
\begin{array}{c}
    x \\
    z
\end{array}
\right] =
\left[
\begin{array}{c}
    x' \\
    z'
\end{array}
\right]
\end{equation}
$$


#### 2. 再由笛卡尔坐标转换为环坐标

$$
\begin{equation}
\begin{array}{rl}
    r= & \sqrt{x'^2+z'^2} \\
     =& \sqrt{(x+\frac{1}{2}z)^2+(\frac{\sqrt{3}}{2}z)^2}\\
\end{array}
\end{equation}
$$

利用 `np.arctan2(y, x)` , 其中 `y` 为纵坐标， `x` 为横坐标，返回从原点到点 $(x,y)$ 的线段与正x轴的角度，返回值为介于 $-\pi$ 到 $\pi$ 之间的弧度值
```python
# axial coordinate (x, z)
import numpy as np
# -pi < angle < pi
angle = np.arctan2(-np.sqrt(3) * z / 2, x + z / 2)
# k: 0, 1, 2, 3, 4, 5
k = round(-angle * 3 / np.pi) % r
```