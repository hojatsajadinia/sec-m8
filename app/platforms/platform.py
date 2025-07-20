
class Platform:
    def __init__(self, platform_name):
        self.platform_name = platform_name
    
    def comment_on_merge_request(self):
        print("Commenting on merge request in platform:", self.platform_name)
