# External
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator


def create_bar_chart(figure, canvas, x, y, x_label, y_label, title):
    figure.clear()
    ax = figure.add_subplot(111)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if len(x) <= 1:
        ax.set_xlim([x[0] - 1, x[0] + 1])
    width = 0.25
    ax.bar(x, y, width, label=x_label)
    ax.legend()
    figure.tight_layout()
    canvas.draw()

def create_graph_chart(figure, canvas, x, y, x_label, y_label, title):
    figure.clear()
    ax = figure.add_subplot(111)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.plot(x, y, label=x_label)
    ax.legend()
    figure.tight_layout()
    canvas.draw()

def create_pie_chart(figure, canvas, values, labels):
    figure.clear()
    ax = figure.add_subplot(111)
    patches, texts, autotexts = ax.pie(values, autopct='%1.1f%%', startangle=90)
    plt.legend(patches, labels, loc='best', fontsize=10)
    canvas.draw()
