        self.lost_woods_img = tk.PhotoImage(file='lost_woods.png')

        # Redimensionar para tamanho 10x10 (ou proporcional mantendo aspect ratio)
        img_width = self.lost_woods_img.width()
        img_height = self.lost_woods_img.height()
        scale_factor = max(img_width/10, img_height/10)
        self.lost_woods_img = self.lost_woods_img.subsample(int(scale_factor))