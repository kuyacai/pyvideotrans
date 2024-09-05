import builtins
import json

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal

from videotrans.configure import config
from videotrans import tts
from videotrans.util import tools

# 使用内置的 open 函数
builtin_open = builtins.open


def open():
    class TestTTS(QThread):
        uito = Signal(str)

        def __init__(self, *, parent=None, text=None):
            super().__init__(parent=parent)
            self.text = text

        def run(self):
            from videotrans.tts import run
            try:
                role = 'alloy'
                if config.params["ai302tts_model"] == 'doubao':
                    role = 'zh_female_shuangkuaisisi_moon_bigtts'
                elif config.params['ai302tts_model'] == 'azure':
                    role = "zh-CN-YunjianNeural"
                run(
                    queue_tts=[{"text":self.text,"role":role,"filename":config.TEMP_HOME + "/testai302tts.mp3","tts_type":tts.AI302_TTS}],
                    language="zh-CN",
                    play=True,
                    is_test=True
                )
                self.uito.emit("ok")
            except Exception as e:
                self.uito.emit(str(e))

    def feed(d):
        if d == "ok":
            QtWidgets.QMessageBox.information(ai302ttsw, "ok", "Test Ok")
        else:
            QtWidgets.QMessageBox.critical(ai302ttsw, config.transobj['anerror'], d)
        ai302ttsw.test_ai302tts.setText('测试')

    def test():
        key = ai302ttsw.ai302tts_key.text().strip()
        model = ai302ttsw.ai302tts_model.currentText()
        if not key or not model:
            return QtWidgets.QMessageBox.critical(ai302ttsw, config.transobj['anerror'],
                                                  '必须填写 302.ai 的API KEY 和 model')
        config.params["ai302tts_key"] = key
        config.params["ai302tts_model"] = model
        task = TestTTS(parent=ai302ttsw, text="你好啊我的朋友")
        ai302ttsw.test_ai302tts.setText('测试中请稍等...')
        task.uito.connect(feed)
        task.start()

    def save():
        key = ai302ttsw.ai302tts_key.text().strip()
        model = ai302ttsw.ai302tts_model.currentText()
        config.params["ai302tts_key"] = key
        config.params["ai302tts_model"] = model
        config.getset_params(config.params)
        ai302ttsw.close()

    def setallmodels():
        t = ai302ttsw.edit_allmodels.toPlainText().strip().replace('，', ',').rstrip(',')
        current_text = ai302ttsw.ai302tts_model.currentText()
        ai302ttsw.ai302tts_model.clear()
        ai302ttsw.ai302tts_model.addItems([x for x in t.split(',') if x.strip()])
        if current_text:
            ai302ttsw.ai302tts_model.setCurrentText(current_text)
        config.settings['ai302tts_models'] = t
        json.dump(config.settings, builtin_open(config.ROOT_DIR + '/videotrans/cfg.json', 'w', encoding='utf-8'),
                  ensure_ascii=False)

    def update_ui():
        config.settings = config.parse_init()
        allmodels_str = config.settings['ai302tts_models']
        allmodels = config.settings['ai302tts_models'].split(',')
        ai302ttsw.ai302tts_model.clear()
        ai302ttsw.ai302tts_model.addItems(allmodels)
        ai302ttsw.edit_allmodels.setPlainText(allmodels_str)
        if config.params["ai302tts_model"] and config.params["ai302tts_model"] in allmodels:
            ai302ttsw.ai302tts_model.setCurrentText(config.params["ai302tts_model"])
        if config.params["ai302tts_key"]:
            ai302ttsw.ai302tts_key.setText(config.params["ai302tts_key"])

    from videotrans.component import AI302TTSForm
    ai302ttsw = config.child_forms.get('ai302ttsw')
    if ai302ttsw is not None:
        ai302ttsw.show()
        update_ui()
        ai302ttsw.raise_()
        ai302ttsw.activateWindow()
        return
    ai302ttsw = AI302TTSForm()
    config.child_forms['ai302ttsw'] = ai302ttsw
    update_ui()
    ai302ttsw.edit_allmodels.textChanged.connect(setallmodels)
    ai302ttsw.set_ai302tts.clicked.connect(save)
    ai302ttsw.test_ai302tts.clicked.connect(test)
    ai302ttsw.show()