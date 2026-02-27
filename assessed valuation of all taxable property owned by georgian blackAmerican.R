library(ggplot2)
library(dplyr)
library(cowplot)

sysfonts::font_add_google(name = "Public Sans", "Public")
showtext::showtext_auto()

options(scipen = 10)

year <- c(1875, 1880, 1885, 1890, 1895, 1899)
valuation_num <- c(5393885, 5764293, 8153390, 12322003, 12941230, 13447423)
diff <- valuation_num - lag(valuation_num, default = 0)
width <- diff
ypos <- rev(cumsum(rev(width)))

df <- data.frame(year, valuation_num, width, ypos)
df2 <- data.frame(1:3)

circle <- ggplot(df, aes(x = 1, y = width, fill = factor(year))) +
  geom_col() +
  scale_fill_manual(values = c("black", "grey60", "#4682b4", "#ffd700", "grey80", "#dc143c")) +
  geom_polygon(data = df2, aes(x = c(1.13, 1.165, 1.15), y = c(ypos[2], ypos[2], 0.8*ypos[1])), fill = "grey60") +
  geom_polygon(data = df2, aes(x = c(0.88, 0.92, 0.90), y = c(ypos[2], ypos[2], 0.8*ypos[1])), fill = "grey60") +
  geom_polygon(data = df2, aes(x = c(0.88, 0.92, 0.90), y = c(ypos[3], ypos[3], 0.8*ypos[1])), fill = "#4682b4") +
  geom_polygon(data = df2, aes(x = c(0.76, 0.79, 0.775), y = c(ypos[2], ypos[2], 0.8*ypos[1])), fill = "grey60") +
  geom_polygon(data = df2, aes(x = c(0.76, 0.79, 0.775), y = c(ypos[3], ypos[3], 0.8*ypos[1])), fill = "#4682b4") +
  geom_polygon(data = df2, aes(x = c(0.76, 0.79, 0.775), y = c(ypos[4], ypos[4], 0.8*ypos[1])), fill = "#ffd700") +
  geom_polygon(data = df2, aes(x = c(0.63, 0.66, 0.645), y = c(ypos[2], ypos[2], 0.8*ypos[1])), fill = "grey60") +
  geom_polygon(data = df2, aes(x = c(0.63, 0.66, 0.645), y = c(ypos[3], ypos[3], 0.8*ypos[1])), fill = "#4682b4") +
  geom_polygon(data = df2, aes(x = c(0.63, 0.66, 0.645), y = c(ypos[4], ypos[4], 0.8*ypos[1])), fill = "#ffd700") +
  geom_polygon(data = df2, aes(x = c(0.63, 0.66, 0.645), y = c(ypos[5], ypos[5], 0.8*ypos[1])), fill = "grey80") +
  geom_polygon(data = df2, aes(x = c(1.33, 1.36, 1.345), y = c(ypos[2], ypos[2], 0.8*ypos[1])), fill = "grey60") +
  geom_polygon(data = df2, aes(x = c(1.33, 1.36, 1.345), y = c(ypos[3], ypos[3], 0.8*ypos[1])), fill = "#4682b4") +
  geom_polygon(data = df2, aes(x = c(1.33, 1.36, 1.345), y = c(ypos[4], ypos[4], 0.8*ypos[1])), fill = "#ffd700") +
  geom_polygon(data = df2, aes(x = c(1.33, 1.36, 1.345), y = c(ypos[5], ypos[5], 0.8*ypos[1])), fill = "grey80") +
  geom_polygon(data = df2, aes(x = c(1.33, 1.36, 1.345), y = c(ypos[6], ypos[6], 0.8*ypos[1])), fill = "#dc143c") +
  scale_y_reverse() +
  coord_polar(theta = "x") +
  theme_void() +
  theme(legend.position = "none")

print(ggdraw(circle))
