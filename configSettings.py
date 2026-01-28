import json
import Global.global_var
import os

class configSettings:
    def __init__(self):
        self.feature_control_config={}
        self.validation_pattern_config={}
        self.comment_pattern_config={}
        return
    def getFeatureControlConfig(self):
        feature_control_config={}
        config_path = os.path.join('configs', 'feature_config.json')
        with open(config_path) as json_file:
            config_dict = json.loads(json_file.read())
        #print(config_dict)
        feature_control_config=config_dict['FeatureControl'][0]
        print(feature_control_config)
        self.feature_control_config=feature_control_config
        return feature_control_config
        
    def getValidationPatternConfig(self):
        validation_pattern_config={}
        config_path = os.path.join('configs', 'Validation_Patterns_config.json')
        with open(config_path) as json_file:
            config_dict = json.loads(json_file.read())
        #print(config_dict)
        validation_pattern_config=config_dict['ValidationPatterns'][0]
        print(validation_pattern_config)
        self.validation_pattern_config=validation_pattern_config
        return validation_pattern_config
        
    def getCommentPatternConfig(self):
        comment_pattern_config=[]
        config_path = os.path.join('configs', 'Comment_Patterns_config.json')
        with open(config_path) as json_file:
            config_dict = json.loads(json_file.read())
        comment_pattern_config=config_dict['CommentPatterns'][0]
        print(comment_pattern_config)
        self.comment_pattern_config=comment_pattern_config
        return comment_pattern_config
        
    def getTracePatternConfig(self):
        trace_pattern_config={}
        config_path = os.path.join('configs', 'Trace_Patterns_config.json')
        with open(config_path) as json_file:
            config_dict = json.loads(json_file.read())
        trace_pattern_config=config_dict['TracePatterns']
        #print(trace_pattern_config)
        self.trace_pattern_config=trace_pattern_config
        return trace_pattern_config

    def getdownloadPipePatternConfig(self):
        downloadPipe_pattern_config={} 
        config_path = os.path.join('configs', 'downloadPipe_Patterns_config.json')
        with open(config_path) as json_file:
            config_dict = json.loads(json_file.read())
        downloadPipe_pattern_config=config_dict['DownloadPipePatterns']
        print(downloadPipe_pattern_config)
        self.downloadPipe_pattern_config=downloadPipe_pattern_config
        return downloadPipe_pattern_config

        
    def createGetLogsFolder(self):
        if(not(os.path.exists(self.feature_control_config["DownloadPath"]))):
            os.makedirs(self.feature_control_config["DownloadPath"], exist_ok=True)
        return
    